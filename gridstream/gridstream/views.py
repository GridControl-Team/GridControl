from tornadio2 import TornadioRouter, SocketConnection
import tornadoredis
import json
import bitarray

class StreamComm(SocketConnection):
	def on_open(self, request):
		print "USER CONNECTED"
		#self.user = request.get_argument("user")
		self.redis = tornadoredis.Client(selected_db=1)
		self.pubsub = tornadoredis.Client(selected_db=1)
		self.pubsub.connect()
		self.pubsub.select(1)
		self.pubsub.subscribe('global_tick', self.on_subscribed)

		self.push_map_update()
		self.push_user_update()
	
	def on_subscribed(self, smt):
		self.pubsub.listen(self.on_redis)
	
	def on_redis(self, msg):
		if msg.kind == 'message':
			s = {'type': 'test', 'content': 'ping'}
			self.send(json.dumps(s))

			self.push_map_update()
			self.push_user_update()

	def push_map_update(self):
		self.redis.get("resource_map", self.on_get_map)

	def on_get_map(self, val):
		print "PUSHING MAP UPDATE TO USER"
		map_data = json.loads(val)
		msg = {
			'type': 'map',
			'content': map_data,
		}
		self.send(json.dumps(msg))

	def push_user_update(self):
		self.redis.get("users_data", self.on_get_users)

	def on_get_users(self, val):
		print "PUSHING USER UPDATE TO USER"
		users = json.loads(val)
		msg = {
			'type': 'users',
			'content': users,
		}
		self.send(json.dumps(msg))
