import random
import operator
import json
import bitarray

from gridlang import GridLangVM, GridLangParser
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
	for i, s in enumerate([16, 16]):
		if new_pos[i] < 0:
			new_pos[i] = (s - 1)
		elif new_pos[i] > (s - 1):
			new_pos[i] = 0
	return new_pos

class GameState(object):
	def __init__(self, map_val, user_val):
		self.map_data = json.loads(map_val)
		self.user_data = json.loads(user_val)

	def spawn_user(self, userid):
		self.user_data[userid] = [5, 5]
	
	def move_user(self, userid, direction):
		old_pos = list(self.user_data.get(userid))
		new_pos = direction_from_pos(direction, old_pos)
		self.user_data[userid] = new_pos
	
	def add_score(self, userid):
		pass
	
	def user_look(self, userid, direction):
		old_pos = list(self.user_data.get(userid))
		new_pos = direction_from_pos(direction, old_pos)
		return self.map_data[new_pos[1]][new_pos[0]]

	def user_pull(self, userid, direction):
		old_pos = list(self.user_data.get(userid))
		new_pos = direction_from_pos(direction, old_pos)
		if self.map_data[new_pos[1]][new_pos[0]] > 0:
			self.map_data[new_pos[1]][new_pos[0]] = 0
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

	def activate_user(self, user_id):
		"""Add user to set of active users.

		The tick_users methods iterates over each of these"""
		self.redis.sadd("active_users", user_id)

	def deactivate_user(self, user_id):
		"""Remove user from set of active users.

		User bot will no longer active on tick_users."""
		self.redis.sdel("active_users", user_id)
	
	def register_code(self, user_id, gist_url):
		gist_retriever = GistRetriever("lol")
		code = gist_retriever.get_file_text(gist_url)
		compiled = GridLangParser.parse(code, constants=GridControlFFI.CONSTANTS)
		frozen = compiled.freeze()
		self.freeze_user_code(user_id, frozen)
	
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
		return True

	def freeze_user_vm(self, user_id, user_vm):
		key = "user_vm_{0}".format(user_id)
		val = json.dumps(user_vm)
		self.redis.set(key, val)
		return True

	def init_map(self):
		map_data = list([0,] * 16 for i in xrange(16))
		allbits = xrange(16 * 16)
		resource_bits = random.sample(allbits, 10)
		print resource_bits
		for r in resource_bits:
			x = r / 16
			y = r % 16
			print x, y
			map_data[x][y] = 1
		self.redis.set("resource_map", json.dumps(map_data))
	
	def tick_environment(self):
		pass

	def tick_user(self, user_id, gamestate):
		print "TICK FOR USER", user_id
		user_vm, user_code = self.thaw_user(user_id)

		if user_code is None:
			# no code?
			print "NO CODE, LOL"
			return

		print "EXECUTING!"
		ffi = GridControlFFI(user_id, gamestate)
		vm = GridLangVM()
		vm.ffi = ffi.call_ffi
		vm.set_code(user_code)
		if user_vm is not None:
			vm.thaw(user_vm)
		#vm.debug = True
		if vm.run(100) == True:
			vm_key = "user_vm_{0}".format(user_id)
			print "USER PROGRAM ENDED, CLEAR VM"
			self.redis.delete(vm_key)
		else:
			print "FREEZING!"
			data = vm.freeze()
			self.freeze_user_vm(user_id, data)
	
	def tick_users(self):
		"""Activate all active users"""
		active_users = self.redis.smembers("active_users")
		if active_users is None:
			return

		resource_map_raw = self.redis.get("resource_map")
		users_data_raw = self.redis.get("users_data")
		if users_data_raw is None:
			users_data_raw = "{}"

		gamestate = GameState(resource_map_raw, users_data_raw)
		
		for userid in active_users:
			if userid not in gamestate.user_data:
				# new user, place them on map somewhere
				gamestate.spawn_user(userid)
			self.tick_user(userid, gamestate)

		gamestate.persist(self.redis)
	
	def emit_tick(self):
		print "EMIT TICK TO STREAMING CLIENTS"
		i = self.redis.publish("global_tick", "tick")
