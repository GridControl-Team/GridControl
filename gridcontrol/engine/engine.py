import random
import operator

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
				user_hash[userid] = (5, 5)
			# blah stupid random walk
			walk = tuple(random.sample([1, 1, -1, -1], 2))
			new_loc = map(operator.add, user_hash[userid], walk)
			for i, s in enumerate([self.WIDTH, self.HEIGHT]):
				if new_loc[i] < 0:
					new_loc[i] = (s - 1)
				elif new_loc[i] > (s - 1):
					new_loc[i] = 0
			user_hash[userid] = "{0},{1}".format(new_loc[0], new_loc[1])
		self.redis.delete("users_hash")
		self.redis.hmset("users_hash", user_hash)
	
	def emit_tick(self):
		print "EMIT TICK"
		i = self.redis.publish("global_tick", "tick")
		print "received:", i
