import random

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
		pad_bit = self.WIDTH * self.HEIGHT + 1
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

		for userid in active_users:
			print "Tick:", userid
	
