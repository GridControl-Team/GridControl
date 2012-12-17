from tornadio2 import TornadioRouter, SocketConnection
import tornadoredis

class StreamComm(SocketConnection):
	def on_open(self, request):
		print "USER CONNECTED"
		self.user = request.get_argument("user")
		self.pubsub = tornadoredis.Client()
		self.pubsub.connect()
		self.pubsub.subscribe('global_tick')
		self.pubsub.listen(self.on_redis)
	
	def on_redis(self, msg):
		if msg.kind == 'message':
			s = "BOOOOOOOYAH"
			self.send(s)

