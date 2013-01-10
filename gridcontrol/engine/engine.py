import random
import operator
import json
import bitarray

from gridlang import GridLangVM, GridLangParser
from gridlang.errors import *
from gridlang.parser import GridLangCode
from gridcontrol.gist_retriever import GistRetriever
from gridcontrol.engine.ffi import GridControlFFI

def direction_from_pos(direction, pos):
	delta = {
		0: [0, -1],
		1: [1, 0],
		2: [0, 1],
		3: [-1, 0],
	}.get(direction)
	new_pos = map(sum, zip(pos, delta))
	for i, s in enumerate([400, 400]):
		if new_pos[i] < 0:
			new_pos[i] = (s - 1)
		elif new_pos[i] > (s - 1):
			new_pos[i] = 0
	return new_pos

def vector_from_pos(vector, pos):
	new_pos = [c % 400 for c in map(sum, zip(pos, vector))]
	return new_pos

def get_random_position(x, y):
	return [random.randint(0, x), random.randint(0, y)]


class GameState(object):
	def __init__(self, engine, map_val, user_val):
		self.engine = engine
		self.map_data = json.loads(map_val)
		self.map_h = len(self.map_data)
		self.map_w = len(self.map_data[0])
		self.user_data = json.loads(user_val)

	def spawn_user(self, userid):
		self.user_data[userid] = get_random_position(self.map_w, self.map_h)
	
	def randomly_spawn_resource(self):
		if random.randint(0, 5) < 2:
			self.spawn_resource()

	def spawn_resource(self):
		x, y = get_random_position(self.map_w-1, self.map_h-1)
		self.map_data[y][x] = 1
	
	def move_user(self, userid, direction):
		old_pos = list(self.user_data.get(userid))
		new_pos = direction_from_pos(direction, old_pos)
		self.user_data[userid] = new_pos
	
	def add_score(self, userid):
		self.engine.add_score(userid)
	
	def user_history(self, userid, cmd, val):
		self.engine.add_history(userid, cmd, val)
	
	def user_look(self, userid, direction):
		old_pos = list(self.user_data.get(userid))
		new_pos = direction_from_pos(direction, old_pos)
		return self.map_data[new_pos[1]][new_pos[0]]

	def user_scan(self, userid, vector):
		old_pos = list(self.user_data.get(userid))
		new_pos = vector_from_pos(vector, old_pos)
		return self.map_data[new_pos[1]][new_pos[0]]

	def user_pull(self, userid, direction):
		old_pos = list(self.user_data.get(userid))
		new_pos = direction_from_pos(direction, old_pos)
		if self.map_data[new_pos[1]][new_pos[0]] > 0:
			self.map_data[new_pos[1]][new_pos[0]] = 0
			self.add_score(userid)
			return 1
		return 0
	
	def persist(self, redis):
		redis.set("users_data", json.dumps(self.user_data))
		redis.set("resource_map", json.dumps(self.map_data))


class GridControlEngine(object):
	WIDTH = 16
	HEIGHT = 16

	def __init__(self, redis):
		self.redis = redis
		self.read_bit = 0
		self.write_bit = 1

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
			compiled = GridLangParser.parse(code, constants=GridControlFFI.CONSTANTS)
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
			user_vm = json.loads(user_vm)
		if user_code is not None:
			frozen_user_code = json.loads(user_code)
			user_code = GridLangCode()
			user_code.thaw(frozen_user_code)
		return user_vm, user_code

	def freeze_user_code(self, user_id, user_code):
		key = "user_code_{0}".format(user_id)
		val = json.dumps(user_code)
		self.redis.set(key, val)
		self.clear_user_vm(user_id)
		return True

	def freeze_user_vm(self, user_id, user_vm):
		key = "user_vm_{0}".format(user_id)
		val = json.dumps(user_vm)
		self.redis.set(key, val)
		return True

	def clear_user_vm(self, user_id):
		key = "user_vm_{0}".format(user_id)
		self.redis.delete(key)

	def init_map(self):
		w = 400
		h = 400
		map_data = list([0,] * w for i in xrange(h))
		allbits = xrange(w * h)
		resource_bits = random.sample(allbits, 400*40)
		for r in resource_bits:
			x = r % w
			y = r / w
			map_data[y][x] = 1
		self.redis.set("resource_map", json.dumps(map_data))
	
	def tick_user(self, user_id, gamestate):
		OP_LIMIT = 400
		print "TICK FOR USER {0}".format(user_id)
		user_vm, user_code = self.thaw_user(user_id)

		if user_code is None:
			# no code?
			print "NO CODE, LOL"
			return

		ffi = GridControlFFI(user_id, gamestate)
		vm = GridLangVM()
		vm.capture_exception = True
		vm.ffi = ffi.call_ffi
		vm.set_code(user_code)
		if user_vm is not None:
			vm.thaw(user_vm)
		#vm.debug = True
		try:
			if vm.run(OP_LIMIT) == True:
				vm_key = "user_vm_{0}".format(user_id)
				print "USER PROGRAM ENDED, CLEAR VM"
				self.redis.delete(vm_key)
			else:
				data = vm.freeze()
				self.freeze_user_vm(user_id, data)
		except GridLangException as e:
			print "USER ERROR, CLEAR VM"
			vm_key = "user_vm_{0}".format(user_id)
			self.redis.delete(vm_key)
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
			if userid not in gamestate.user_data:
				# new user, place them on map somewhere
				gamestate.spawn_user(userid)
			try:
				self.tick_user(userid, gamestate)
			except GridLangException as e:
				print "USER {0} HAD VM ISSUE".format(userid)
				channel = "user_msg_{0}".format(userid)
				msg = "{0}\n\n{1}".format(e.traceback, e.message)
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
