from tornadio2 import TornadioRouter, SocketConnection
import tornadoredis
import simplejson as json
from collections import namedtuple

class StateHolder(object):
	def __init__(self):
		self.usernames = {}
		self.userscores = {}
		self.redis = tornadoredis.Client(selected_db=1)
		self.pubsub = tornadoredis.Client(selected_db=1)
		self.pubsub.connect()
		self.pubsub.select(1)
		self.pubsub.subscribe('global_tick', self.on_subscribed)
		self.c = 2
		self.redis.hgetall("user_usernames", self.on_get_usernames)
		self.redis.get("user_attr", self.on_get_userattr)
	
	def on_subscribed(self, smt):
		self.pubsub.listen(self.on_redis)

	def on_redis(self, msg):
		print "on_redis"
		if msg.kind == 'message':
			if msg.channel == 'global_tick' and msg.body == 'tick':
				if self.c != 0:
					return
				self.c = 2
				self.redis.hgetall("user_usernames", self.on_get_usernames)
				self.redis.get("user_attr", self.on_get_userattr)

	def on_get_usernames(self, val):
		self.usernames = val
		self.next()
	
	def on_get_userattr(self, val):
		self.userattr = json.loads(val, use_decimal=True)
		self.userscores = {}
		for k, v in self.userattr.iteritems():
			if k.endswith(":resources"):
				uid = k.split(":")[0]
				self.userscores[uid] = v
		self.next()

	def next(self):
		self.c = self.c - 1
		if self.c == 0:
			self.redis.publish('global_tick', 'tock')
	
SH = StateHolder()
	
class StreamComm(SocketConnection):
	def on_open(self, request):
		print "USER CONNECTED"
		try:
			self.userid = int(request.get_argument("userid"))
		except (TypeError, ValueError) as e:
			self.userid = None

		global SH
		self.state = SH
		self.last_history_ts = None

		self.redis = tornadoredis.Client(selected_db=1)
		self.pubsub = tornadoredis.Client(selected_db=1)
		self.pubsub.connect()
		self.pubsub.select(1)
		if self.userid is not None:
			channels = ['global_tick', 'user_msg_{0}'.format(self.userid)]
		else:
			channels = ['global_tick',]
		self.pubsub.subscribe(channels, self.on_subscribed)

		self.push_usernames()
		self.push_userscores()
		self.push_user_history()
	
	def on_close(self):
		self.userid = None
		self.last_history_ts = None
		self.state = None
		self.redis.disconnect()
		self.pubsub.disconnect()
	
	def on_subscribed(self, smt):
		self.pubsub.listen(self.on_redis)

	def on_redis(self, msg):
		if msg.kind == 'message':
			if msg.channel == 'global_tick':
				if msg.body == 'tock':
					pass
			elif msg.channel == 'user_msg_{0}'.format(self.userid):
				self.push_user_update(msg.body)
				self.push_usernames()
				self.push_userscores()
				self.push_user_history()

	def push_usernames(self):
		msg = {
			'type': 'username',
			'content': self.state.usernames,
		}
		self.send(json.dumps(msg, use_decimal=True))

	def push_userscores(self):
		msg = {
			'type': 'scores',
			'content': self.state.userscores,
		}
		self.send(json.dumps(msg, use_decimal=True))

	def push_user_update(self, val):
		print "sending:", val
		self.send(val)

	def push_user_history(self):
		self.redis.lrange("user_history_{0}".format(self.userid), 0, 15, self.on_user_history)
	
	def on_user_history(self, val):
		history = []

		for hitem in val:
			hspec = json.loads(hitem, use_decimal=True)
			if hspec.get('ts', 0) > self.last_history_ts:
				history.append(hspec)

		if len(history):
			self.last_history_ts = history[0].get('ts')

		msg = {
			'type': 'history',
			'content': history,
		}
		self.send(json.dumps(msg, use_decimal=True))

