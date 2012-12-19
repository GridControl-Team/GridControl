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
		ba = bitarray.bitarray()
		try:
			ba.frombytes(val)
		except UnicodeDecodeError:
			# didn't have property data here
			return
		rmap = map(int, ba.tolist())
		msg = {
			'type': 'map',
			'content': rmap,
		}
		self.send(json.dumps(msg))

	def push_user_update(self):
		self.redis.hgetall("users_hash", self.on_get_user)

	def on_get_user(self, val):
		print "PUSHING USER UPDATE TO USER"
		user_hash = {}
		for k, v in val.iteritems():
			user_hash[k] = tuple(int(i) for i in v.split(","))
		msg = {
			'type': 'users',
			'content': user_hash,
		}
		self.send(json.dumps(msg))
