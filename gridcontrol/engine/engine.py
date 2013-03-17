import random
import operator
import simplejson as json
import time
import requests
from collections import namedtuple

import traceback
import sys

from gridlang import GridLangVM, GridLangParser
from gridlang.errors import *
from gridlang.parser import GridLangCode
from gridcontrol.gist_retriever import GistRetriever
from gridcontrol.engine.ffi import GridControlFFI, CONSTANTS, pluck, ATTRS, STATUS
from django.conf import settings

MAP_WIDTH = 400
MAP_HEIGHT = 400

GridObj = namedtuple("GridObj", ['t', 'i', 'x', 'y'])

def direction_from_pos(direction, pos):
	delta = {
		1: (0, -1),
		2: (1, 0),
		3: (0, 1),
		4: (-1, 0),
	}.get(direction, (0, 0))
	new_pos = ((pos[0] + delta[0]) % MAP_WIDTH, (pos[1] + delta[1]) % MAP_HEIGHT)
	return new_pos

def vector_from_pos(vector, pos):
	new_pos = ((pos[0] + vector[0]) % MAP_WIDTH, (pos[1] + vector[1]) % MAP_HEIGHT)
	return new_pos

def get_random_position(x, y):
	return (random.randint(0, x), random.randint(0, y))


class GameState(object):
	def __init__(self, engine, pos_val, user_attr):
		self.engine = engine
		self.map_h = MAP_HEIGHT
		self.map_w = MAP_WIDTH
		if user_attr is not None:
			self.user_attr = json.loads(user_attr)
		else:
			self.user_attr = {}
		self.pos_obj = {}
		self.user_pos = {}
		if pos_val is not None:
			pos_obj = json.loads(pos_val, use_decimal=True)
			def_obj = {'t':None, 'i':None, 'x':None, 'y':None}
			for v in pos_obj:
				_v = dict(def_obj)
				_v.update(v)
				obj = GridObj(**_v)
				pos = (obj.x, obj.y)
				self.pos_obj[pos] = obj
				if obj.t == CONSTANTS.get('CELL_ROBOT'):
					self.user_pos[obj.i] = pos
					if obj.i == 1:
						print "In load: {0}".format(repr(pos))
		else:
			self.init_resources()

	def init_resources(self):
		for x in xrange((MAP_WIDTH * MAP_HEIGHT) / 4):
			self.spawn_resource()
		for x in xrange((MAP_WIDTH * MAP_HEIGHT) / 8):
			self.spawn_rock()

	def spawn_user(self, user_id):
		pos = self.get_open_position()
		if pos is None:
			raise GridLangException("Could not locate empty space for you! Sorry! It will try again next tick.")
		self.user_pos[user_id] = pos
		self.pos_obj[pos] = GridObj(t=CONSTANTS.get("CELL_ROBOT"), i=user_id, x=pos[0], y=pos[1])

	def randomly_spawn_resource(self):
		for i in xrange(4):
			if random.randint(0, 5) < 2:
				self.spawn_resource()

	def spawn_resource(self):
		pos = self.get_open_position()
		if pos is not None:
			self.pos_obj[pos] = GridObj(t=CONSTANTS.get("CELL_RESOURCE"), i=None, x=pos[0], y=pos[1])
	
	def spawn_rock(self):
		pos = self.get_open_position()
		if pos is not None:
			self.pos_obj[pos] = GridObj(t=CONSTANTS.get("CELL_ROCK"), i=None, x=pos[0], y=pos[1])
	
	def obj_at(self, x, y):
		pos = (x, y)
		if pos in self.pos_obj:
			return self.pos_obj[pos].t
		return CONSTANTS.get('CELL_EMPTY')

	def user_at(self, x, y):
		pos = (x, y)
		if pos in self.pos_obj and self.pos_obj[pos].t == CONSTANTS.get("CELL_ROBOT"):
			return self.pos_obj[pos].i
	
	def get_open_position(self):
		for i in xrange(1000):
			pos = get_random_position(self.map_w-1, self.map_h-1)
			if self.obj_at(*pos) == 0:
				return pos
		return None
	
	def add_resource(self, user_id):
		self.incr_user_attr(user_id, "resources", 1)
	
	def user_history(self, user_id, cmd, val, success):
		self.engine.add_history(user_id, cmd, val, success)
	
	def do_user_move(self, user_id, direction):
		self.incr_user_attr(user_id, "charge", -5)
		old_pos = self.user_pos[user_id]
		new_pos = direction_from_pos(direction, old_pos)
		if self.obj_at(*new_pos) == 0:
			self.user_pos[user_id] = new_pos
			self.pos_obj[new_pos] = GridObj(t=CONSTANTS.get("CELL_ROBOT"), i=user_id, x=new_pos[0], y=new_pos[1])
			del self.pos_obj[old_pos]
			if user_id == 1:
				print "after move: old:{0} new:{1} user_pos:{2}".format(repr(old_pos), repr(new_pos), repr(self.user_pos[1]))
			return 1
		return 0

	def do_obj_move(self, pos, direction):
		new_pos = direction_from_pos(direction, pos)
		old_obj = self.pos_obj[pos]
		obj = GridObj(
			t = old_obj.t,
			i = old_obj.i,
			x = new_pos[0],
			y = new_pos[1],
		)
		self.pos_obj[new_pos] = obj
		del self.pos_obj[pos]
	
	def do_user_look(self, user_id, direction):
		old_pos = list(self.user_pos.get(user_id))
		new_pos = direction_from_pos(direction, old_pos)
		return self.obj_at(*new_pos)

	def do_user_locate(self, user_id):
		return self.user_pos.get(user_id, [-1, -1])

	def do_user_scan(self, user_id, x, y):
		old_pos = list(self.user_pos.get(user_id))
		new_pos = vector_from_pos([x, y], old_pos)
		return self.obj_at(*new_pos)

	def do_user_pull(self, user_id, direction):
		old_pos = list(self.user_pos.get(user_id))
		new_pos = direction_from_pos(direction, old_pos)
		if self.obj_at(*new_pos) == CONSTANTS.get("CELL_RESOURCE"):
			del self.pos_obj[new_pos]
			self.add_resource(user_id)
			return 1
		return 0

	def do_user_push(self, user_id, direction):
		self.incr_user_attr(user_id, "charge", -10)
		old_pos = self.user_pos[user_id]
		new_pos = direction_from_pos(direction, old_pos)
		target = self.obj_at(*new_pos)
		if target in (CONSTANTS.get("CELL_ROCK"), CONSTANTS.get("CELL_ROBOT")):
			new_posb = direction_from_pos(direction, new_pos)
			if self.obj_at(*new_posb) == 0:
				self.do_obj_move(new_pos, direction)
				self.do_user_move(user_id, direction)
				return 1
		return 0

	def do_user_punch(self, user_id, direction):
		self.incr_user_attr(user_id, "charge", -10)
		old_pos = self.user_pos[user_id]
		new_pos = direction_from_pos(direction, old_pos)
		target = self.user_at(*new_pos)
		if target is not None:
			self.user_history(target, "YOUR BOT", "WAS ATTACKED", 0)
			self.kill_user(target)
			self.pos_obj[new_pos] = GridObj(t=CONSTANTS.get("CELL_RESOURCE"), i=None, x=new_pos[0], y=new_pos[1])
			return 1
		return 0

	def do_user_chargeup(self, user_id, val):
		charge = self.get_user_attr(user_id, "charge")
		resources = self.get_user_attr(user_id, "resources")
		try:
			val = int(val)
		except ValueError, TypeError:
			return 0

		if val > resources:
			self.user_history(user_id, "BOT CHARGE", "LACKS RESOURCES", 0)
			ret = 0
		else:
			self.incr_user_attr(user_id, "resources", -val)
			if (val > 10) or ((charge + val) > 50):
				self.user_history(user_id, "BOT CHARGE", "EXCESSIVE", 0)
				self.kill_user(user_id)
				ret = 0
			else:
				self.set_user_attr(user_id, "charge", charge + val)
				ret = 1
		return ret

	def do_user_inspect(self, user_id, direction, attr):
		old_pos = list(self.user_pos.get(user_id))
		new_pos = direction_from_pos(direction, old_pos)
		target = self.user_at(*new_pos)
		attr_s = pluck(attr, ATTRS)
		ret = self.get_user_attr(target, attr_s)
		return ret

	def do_user_pewpew(self, user_id, direction):
		charge = self.get_user_attr(user_id, "charge")
		steps = charge / 10
		if steps < 1:
			self.user_history(user_id, "PEWPEW", "LACKS ENERGY", 0)
			self.set_user_attr(user_id, "charge", 0)
			return 0
		old_pos = list(self.user_pos.get(user_id))
		for i in range(steps):
			new_pos = direction_from_pos(direction, old_pos)
			target = self.user_at(*new_pos)
			if target is not None:
				self.user_history(target, "YOUR BOT", "WAS LASERED", 0)
				self.kill_user(target)
			old_pos = new_pos
		self.set_user_attr(user_id, "charge", 0)
		return 1

	def do_user_selfdestruct(self, user_id):
		self.kill_user(user_id)
		return 1

	def get_user_attr(self, user_id, attr):
		key = "{0}:{1}".format(user_id, attr.lower())
		return self.user_attr.get(key, 0)

	def set_user_attr(self, user_id, attr, val):
		key = "{0}:{1}".format(user_id, attr)
		self.user_attr[key] = val

	def incr_user_attr(self, user_id, attr, val):
		key = "{0}:{1}".format(user_id, attr)
		old_val = self.user_attr.get(key, 0)
		self.user_attr[key] = max(old_val + val, 0)
	
	def is_user_dead(self, user_id):
		v = self.get_user_attr(user_id, "status")
		return v == CONSTANTS.get("DEAD")

	def kill_user(self, user_id):
		self.set_user_attr(user_id, "status", CONSTANTS.get("DEAD"))
		old_pos = self.user_pos[user_id]
		del self.user_pos[user_id]
		del	self.pos_obj[old_pos]
		self.user_history(user_id, "YOUR BOT", "HAS DIED", 0)
		self.set_user_attr(user_id, "charge", 0)
	
	def clear_status(self, user_id):
		self.set_user_attr(user_id, "status", 0)
	
	def get_map_for(self, user_id):
		map_r = 5
		if user_id in self.user_pos:
			x, y = self.user_pos[user_id]
			m = []
			for y2 in xrange(y-map_r, y+map_r + 1):
				l = []
				for x2 in xrange(x-map_r, x+map_r + 1):
					y3 = y2 % self.map_h
					x3 = x2 % self.map_w
					pos = (x3, y3)
					if pos in self.pos_obj:
						obj = self.pos_obj[pos]
						if obj.t == 3:
							l.append({'t':3, 'i':obj.i})
						else:
							l.append({'t':obj.t})
					else:
						l.append({'t':0})
				m.append(l)
			if user_id == 1:
				print "user at: {0}, {1}".format(x, y)
			return m
		else:
			return []
	
	def persist(self, redis):
		redis.set("users_data", json.dumps(self.user_pos))
		redis.set("user_attr", json.dumps(self.user_attr))
		pos_obj = [v._asdict() for k,v in self.pos_obj.iteritems()]
		print "in persist: {0}".format(repr(self.user_pos[1]))
		redis.set("position_map", json.dumps(pos_obj))


class GridControlEngine(object):
	WIDTH = 16
	HEIGHT = 16

	def __init__(self, redis, line_limit=None, const_limit=None, data_limit=None, reg_limit=None, exe_limit=None):
		self.redis = redis
		self.read_bit = 0
		self.write_bit = 1
		self.data_limit = data_limit
		self.reg_limit = reg_limit
		self.exe_limit = exe_limit
		self.line_limit = line_limit
		self.const_limit = const_limit
	
	def is_user_active(self, user_id):
		return self.redis.sismember("active_users", user_id)

	def activate_user(self, user_id, username):
		"""Add user to set of active users.

		The tick_users methods iterates over each of these"""
		self.redis.sadd("active_users", user_id)
		self.redis.hset("user_usernames", user_id, username)

	def deactivate_user(self, user_id):
		"""Remove user from set of active users.

		User bot will no longer active on tick_users."""
		self.redis.srem("active_users", user_id)

	def fetch_code(self, user_id, raw_url):
		retriever = GistRetriever('dforsyth is the best')
		code = retriever.get_file_text(raw_url)

		if raw_url.upper().endswith('.GRIDLANG'):
			return code, None

		if raw_url.upper().endswith('.GRIDC'):
			resp = requests.post(settings.GRIDC_COMPILER_URI, data=code)
			if resp.status_code == requests.codes.ok:
				return resp.text, 'gridc resp: %d' % resp.status_code

		return None, None

	def register_code(self, user_id, raw_url):
		code, err = self.fetch_code(user_id, raw_url)
		if not code:
			if err:
				return False, err
			return False, 'Failed to fetch code from %s' % raw_url

		try:
			compiled = GridLangParser.parse(
				code,
				constants = CONSTANTS,
				line_limit = self.line_limit,
				const_limit = self.const_limit,
			)
			frozen = compiled.freeze()
			self.freeze_user_code(user_id, frozen)
			return True, ""
		except GridLangParseException as e:
			return False, str(e)

	def add_history(self, user_id, cmd, val, success):
		ts = int(time.time())
		key = "user_history_{0}".format(user_id)
		spec = {
			'cmd': cmd,
			'val': val,
			'ts': ts,
			'success': success,
		}
		hval = json.dumps(spec, use_decimal=True)
		l = self.redis.lpush(key, hval)
		self.redis.ltrim(key, 0, 10)
	
	def thaw_user(self, user_id):
		vm_key = "user_vm_{0}".format(user_id)
		code_key = "user_code_{0}".format(user_id)
		user_vm = self.redis.get(vm_key)
		user_code = self.redis.get(code_key)
		if user_vm is not None:
			user_vm = json.loads(user_vm, use_decimal=True)
		if user_code is not None:
			frozen_user_code = json.loads(user_code, use_decimal=True)
			user_code = GridLangCode()
			user_code.thaw(frozen_user_code)
		return user_vm, user_code

	def get_user_code(self, user_id):
		key = "user_code_{0}".format(user_id)
		val = self.redis.get(key)
		if val is not None:
			return json.loads(val, use_decimal=True)
		else:
			return []

	def get_user_vm(self, user_id):
		key = "user_vm_{0}".format(user_id)
		val = self.redis.get(key)
		if val is not None:
			return json.loads(val, use_decimal=True)
		else:
			return {}

	def freeze_user_code(self, user_id, user_code):
		key = "user_code_{0}".format(user_id)
		val = json.dumps(user_code, use_decimal=True)
		self.redis.set(key, val)
		self.clear_user_vm(user_id)
		return True

	def freeze_user_vm(self, user_id, user_vm):
		key = "user_vm_{0}".format(user_id)
		val = json.dumps(user_vm, use_decimal=True)
		self.redis.set(key, val)
		return True

	def clear_user_vm(self, user_id):
		key = "user_vm_{0}".format(user_id)
		self.redis.delete(key)

	def set_user_view(self, user_id, gamestate):
		key = "user_msg_{0}".format(user_id)
		user_map = gamestate.get_map_for(user_id)
		val = json.dumps({
			'type': 'map',
			'content': user_map,
		})
		self.redis.publish(key, val)

	def reparse_all_users(self):
		active_users = self.redis.smembers("active_users")
		if active_users is None:
			return
		for user_id in active_users:
			key = "user_code_{0}".format(user_id)
			val = self.redis.get(key)
			if val is not None:
				c = json.loads(val, use_decimal=True)
			else:
				continue

			code = c.get('raw', None)
			if code is None:
				continue

			try:
				compiled = GridLangParser.parse(
					code,
					constants = CONSTANTS,
					line_limit = self.line_limit,
					const_limit = self.const_limit,
				)
				frozen = compiled.freeze()
				self.freeze_user_code(user_id, frozen)
			except GridLangParseException as e:
				pass
	

	def tick_user(self, user_id, gamestate):
		OP_LIMIT = 400
		#print "TICK FOR USER {0}".format(user_id)
		user_vm, user_code = self.thaw_user(user_id)

		if user_code is None:
			# no code?
			print "NO CODE, LOL"
			self.deactivate_user(user_id)
			return

		ffi = GridControlFFI(user_id, gamestate)
		vm = GridLangVM()
		vm.data_limit = self.data_limit
		vm.exe_limit = self.exe_limit
		vm.reg_limit = self.reg_limit
		vm.capture_exception = True
		vm.ffi = ffi.call_ffi
		vm.set_code(user_code)
		if user_vm is not None:
			flags = user_vm.get('flags')
			if not len(set(flags) & set(["end", "crash"])):
				vm.thaw(user_vm)
		#vm.debug = True
		try:
			if vm.run(OP_LIMIT) == True:
				vm.flags.add("end")
			data = vm.freeze()
			self.freeze_user_vm(user_id, data)
		except GridLangException as e:
			print "USER ERROR, MARKING DIRTY"
			vm.flags.add("crash")
			data = vm.freeze()
			self.freeze_user_vm(user_id, data)
			raise e
	
	def do_tick(self):
		"""Activate all active users"""
		global_lock = self.redis.setnx("global_lock", "#yolo")
		if not global_lock:
			print "execution locked"
			return False
		active_users = self.redis.smembers("active_users")
		if active_users is None:
			return True
		active_users = map(int, active_users)

		position_map_raw = self.redis.get("position_map")
		user_attr_raw = self.redis.get("user_attr")

		gamestate = GameState(self, position_map_raw, user_attr_raw)

		# tick environment
		gamestate.randomly_spawn_resource()
		
		# tick all users
		for user_id in active_users:
			if gamestate.is_user_dead(user_id):
				gamestate.clear_status(user_id)
				gamestate.spawn_user(user_id)
				continue
			try:
				if user_id not in gamestate.user_pos:
					# new user, place them on map somewhere
					gamestate.spawn_user(user_id)
					# also restart their vm
					self.clear_user_vm(user_id)
				self.tick_user(user_id, gamestate)
			except GridLangException as e:
				print "USER {0} HAD VM ISSUE".format(user_id)
				channel = "user_msg_{0}".format(user_id)
				if hasattr(e, 'traceback'):
					msg = "{0}\n\n{1}".format(e.traceback, e.message)
				else:
					msg = e.message
				self.redis.publish(channel, json.dumps({
					'type': 'exception',
					'content': msg,
				}))
			except Exception as e:
				print "USER {0} HAS UNCAUGHT ISSUE".format(user_id)
				exc_type, exc_value, exc_traceback = sys.exc_info()
				traceback.print_exception(type(e), e, exc_traceback)
				channel = "user_msg_{0}".format(user_id)
				msg = "{0}\n\n{1}".format("GRIDLANG Exception", e.message)
				self.redis.publish(channel, msg)

		for user_id in active_users:
			self.set_user_view(user_id, gamestate)

		gamestate.persist(self.redis)
		self.emit_tick()
		self.redis.delete("global_lock")
		return True
	
	def emit_tick(self):
		#print "EMIT TICK TO STREAMING CLIENTS"
		i = self.redis.publish("global_tick", "tick")
