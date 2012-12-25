import random
import operator

from gridlang import GridLangVM

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
	
	def thaw_user(self, user_id):
		vm_key = "user_vm_{0}".format(user_id)
		code_key = "user_code_{0}".format(user_id)
		user_vm = self.redis.get(vm_key)
		user_code = self.redis.get(code_key)
		if user_vm is not None:
			user_vm = json.loads(user_vm)
		if user_code is not None:
			user_code = json.loads(user_code)
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
		print "Clearing Map"
		pad_bit = self.WIDTH * self.HEIGHT + 1
		self.redis.set("resource_map", 0)
		self.redis.setbit("resource_map", pad_bit, 0)
		allbits = xrange(self.WIDTH * self.HEIGHT)
		resource_bits = random.sample(allbits, 10)
		for r in resource_bits:
			self.redis.setbit("resource_map", r, 1)
	
	def tick_environment(self):
		pass

	def tick_user(self, user_id):
		print "TICK FOR USER", user_id
		user_vm, user_code = self.thaw_user(user_id)

		if user_code is None:
			# no code?
			print "NO CODE, LOL"
			return

		print "EXECUTING!"
		vm = GridLangVM()
		vm.set_code(user_code)
		if user_vm is not None:
			vm.thaw(user_vm)
		vm.debug = True
		vm.run(10)

		print "FREEZING!"
		data = vm.freeze()
		self.freeze_user_vm(data)
	
	def __old_random_walk(self):
		# blah stupid random walk
		walk = tuple(random.sample([1, 1, -1, -1], 2))
		new_loc = map(operator.add, user_hash[userid], walk)
		for i, s in enumerate([self.WIDTH, self.HEIGHT]):
			if new_loc[i] < 0:
				new_loc[i] = (s - 1)
			elif new_loc[i] > (s - 1):
				new_loc[i] = 0
		user_hash[userid] = "{0},{1}".format(new_loc[0], new_loc[1])

	def tick_users(self):
		"""Activate all active users"""
		active_users = self.redis.smembers("active_users")
		if active_users is None:
			return

		user_hash_raw = self.redis.hgetall("users_hash")
		user_hash = {}
		for k, v in user_hash_raw.iteritems():
			user_hash[k] = tuple(int(i) for i in v.split(","))
		
		for userid in active_users:
			if userid not in user_hash:
				# new user, place them on map somewhere
				user_hash[userid] = (5, 5)
			self.tick_user(userid)

			# blah
			new_loc = [5, 5]
			user_hash[userid] = "{0},{1}".format(new_loc[0], new_loc[1])
		self.redis.delete("users_hash")
		self.redis.hmset("users_hash", user_hash)
	
	def emit_tick(self):
		print "EMIT TICK"
		i = self.redis.publish("global_tick", "tick")
		print "received:", i
