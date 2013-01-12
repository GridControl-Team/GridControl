import random
import operator
import simplejson as json

from gridlang import GridLangVM, GridLangParser
from gridlang.errors import *
from gridlang.parser import GridLangCode
from gridcontrol.gist_retriever import GistRetriever
from gridcontrol.engine.ffi import GridControlFFI

MAP_WIDTH = 11
MAP_HEIGHT = 11

def direction_from_pos(direction, pos):
	delta = {
		0: [0, -1],
		1: [1, 0],
		2: [0, 1],
		3: [-1, 0],
	}.get(direction)
	new_pos = [(pos[0] + delta[0]) % MAP_WIDTH, (pos[1] + delta[1]) % MAP_HEIGHT]
	return new_pos

def vector_from_pos(vector, pos):
	new_pos = [(pos[0] + vector[0]) % MAP_WIDTH, (pos[1] + vector[1]) % MAP_HEIGHT]
	return new_pos

def get_random_position(x, y):
	return [random.randint(0, x), random.randint(0, y)]


class GameState(object):
	def __init__(self, engine, map_val, user_val):
		self.engine = engine
		self.map_h = MAP_HEIGHT
		self.map_w = MAP_WIDTH
		if map_val is not None:
			self.map_data = json.loads(map_val)
			self.user_pos = json.loads(user_val)
			self.pos_user = dict((tuple(v), k) for k, v in self.user_pos.iteritems())
		else:
			self.user_pos = {}
			self.pos_user = {}
			self.init_map()
			self.init_resources()


	def init_map(self):
		map_data = list([0,] * MAP_WIDTH for i in xrange(MAP_HEIGHT))
		self.map_data = map_data
	
	def init_resources(self):
		for x in xrange((MAP_WIDTH * MAP_HEIGHT) / 4):
			self.spawn_resource()

	def spawn_user(self, userid):
		pos = self.get_open_position()
		if pos is None:
			raise GridLangException("Could not locate empty space for you! Sorry! It will try again next tick.")
		self.user_pos[userid] = pos
		self.pos_user[pos] = userid
	
	def obj_at(self, x, y):
		m = self.map_data[y][x]
		if m == 0 and (x, y) in self.pos_user:
			return 10
		return m

	def user_at(self, x, y):
		c = (x, y)
		if c in self.pos_user:
			return self.pos_user[c]
	
	def get_open_position(self):
		for i in xrange(1000):
			pos = get_random_position(self.map_w-1, self.map_h-1)
			if self.obj_at(*pos) == 0:
				return pos
		return None
	
	def randomly_spawn_resource(self):
		if random.randint(0, 5) < 2:
			self.spawn_resource()

	def spawn_resource(self):
		pos = self.get_open_position()
		if pos is not None:
			self.map_data[pos[1]][pos[0]] = 1
	
	def move_user(self, userid, direction):
		old_pos = list(self.user_pos.get(userid))
		new_pos = direction_from_pos(direction, old_pos)
		if self.obj_at(*new_pos) == 0:
			self.user_pos[userid] = new_pos
			self.pos_user[tuple(new_pos)] = userid
			del self.pos_user[tuple(old_pos)]
			return 1
		return 0
	
	def add_score(self, userid):
		self.engine.add_score(userid)
	
	def user_history(self, userid, cmd, val):
		self.engine.add_history(userid, cmd, val)
	
	def user_look(self, userid, direction):
		old_pos = list(self.user_pos.get(userid))
		new_pos = direction_from_pos(direction, old_pos)
		return self.obj_at(*new_pos)

	def user_locate(self, userid, direction):
		return self.user_pos.get(userid, [-1, -1])

	def user_scan(self, userid, vector):
		old_pos = list(self.user_pos.get(userid))
		new_pos = vector_from_pos(vector, old_pos)
		return self.obj_at(*new_pos)

	def user_pull(self, userid, direction):
		old_pos = list(self.user_pos.get(userid))
		new_pos = direction_from_pos(direction, old_pos)
		if self.obj_at(*new_pos) == 1:
			self.map_data[new_pos[1]][new_pos[0]] = 0
			self.add_score(userid)
			return 1
		return 0

	def user_push(self, userid, direction):
		old_pos = list(self.user_pos.get(userid))
		new_pos = direction_from_pos(direction, old_pos)
		target = self.user_at(*new_pos)
		if target is not None:
			new_posb = direction_from_pos(direction, new_pos)
			if self.obj_at(*new_posb) == 0:
				self.move_user(target, direction)
				self.move_user(userid, direction)
				return 1
		return 0

	
	def persist(self, redis):
		redis.set("users_data", json.dumps(self.user_pos))
		redis.set("resource_map", json.dumps(self.map_data))


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
	
	def register_code(self, user_id, gist_url):
		gist_retriever = GistRetriever("lol")
		code = gist_retriever.get_file_text(gist_url)
		try:
			compiled = GridLangParser.parse(
				code,
				constants = GridControlFFI.CONSTANTS,
				line_limit = self.line_limit,
				const_limit = self.const_limit,
			)
			frozen = compiled.freeze()
			self.freeze_user_code(user_id, frozen)
			return True, ""
		except GridLangParseException as e:
			return False, str(e)

	def add_score(self, user_id):
		self.redis.hincrby("user_scores", user_id, 1)
	
	def add_history(self, user_id, cmd, val):
		key = "user_history_{0}".format(user_id)
		hval = "{0}:{1}".format(cmd, val)
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

	def tick_user(self, user_id, gamestate):
		OP_LIMIT = 400
		print "TICK FOR USER {0}".format(user_id)
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
			if not ('end' in flags or 'crash' in flags):
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
		active_users = self.redis.smembers("active_users")
		if active_users is None:
			return

		resource_map_raw = self.redis.get("resource_map")
		users_data_raw = self.redis.get("users_data")
		if users_data_raw is None:
			users_data_raw = "{}"

		gamestate = GameState(self, resource_map_raw, users_data_raw)

		# tick environment
		gamestate.randomly_spawn_resource()
		
		# tick all users
		for userid in active_users:
			try:
				if userid not in gamestate.user_pos:
					# new user, place them on map somewhere
					gamestate.spawn_user(userid)
				self.tick_user(userid, gamestate)
			except GridLangException as e:
				print "USER {0} HAD VM ISSUE".format(userid)
				channel = "user_msg_{0}".format(userid)
				if hasattr(e, 'traceback'):
					msg = "{0}\n\n{1}".format(e.traceback, e.message)
				else:
					msg = e.message
				self.redis.publish(channel, msg)
			except Exception as e:
				print "USER {0} HAS UNCAUGHT ISSUE".format(userid)
				print e
				channel = "user_msg_{0}".format(userid)
				msg = "{0}\n\n{1}".format("GRIDLANG Exception", e.message)
				self.redis.publish(channel, msg)

		gamestate.persist(self.redis)
	
	def emit_tick(self):
		print "EMIT TICK TO STREAMING CLIENTS"
		i = self.redis.publish("global_tick", "tick")
