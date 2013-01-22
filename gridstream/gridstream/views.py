from tornadio2 import TornadioRouter, SocketConnection
import tornadoredis
import simplejson as json
from collections import namedtuple

MapObj = namedtuple("MapObj", ['x', 'y', 't', 'i'])

def makeMapObj(d):
	return MapObj(
		d.get('x'),
		d.get('y'),
		d.get('t'),
		d.get('i'),
	)

class StateHolder(object):
	def __init__(self):
		self.usernames = {}
		self.map_data = []
		self.userscores = {}
		self.user_pos = {}
		self.pos_user = {}
		self.redis = tornadoredis.Client(selected_db=1)
		self.pubsub = tornadoredis.Client(selected_db=1)
		self.pubsub.connect()
		self.pubsub.select(1)
		self.pubsub.subscribe('global_tick', self.on_subscribed)
		self.c = 3
		self.redis.hgetall("user_usernames", self.on_get_usernames)
		self.redis.get("user_attr", self.on_get_userattr)
		self.redis.get("position_map", self.on_get_map)
	
	def on_subscribed(self, smt):
		self.pubsub.listen(self.on_redis)

	def on_redis(self, msg):
		if msg.kind == 'message':
			if msg.channel == 'global_tick' and msg.body == 'tick':
				if self.c != 0:
					return
				self.c = 3
				self.redis.hgetall("user_usernames", self.on_get_usernames)
				self.redis.get("user_attr", self.on_get_userattr)
				self.redis.get("position_map", self.on_get_map)

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

	def on_get_map(self, val):
		pos_obj = json.loads(val, use_decimal=True)
		self.pos_obj = dict((tuple(map(int, k.split(","))), makeMapObj(v)) for k, v in pos_obj.iteritems())
		self.user_pos = dict((v.i, k) for k, v in self.pos_obj.iteritems() if v.t == 3)
		self.map_h = 400
		self.map_w = 400
		self.next()

	def next(self):
		self.c = self.c - 1
		if self.c == 0:
			self.redis.publish('global_tick', 'tock')
	
	def get_map_for(self, userid):
		uid = str(userid)
		map_r = 5
		if uid in self.user_pos:
			x, y = self.user_pos[uid]
			m = []
			for y2 in xrange(y-map_r, y+map_r + 1):
				l = []
				for x2 in xrange(x-map_r, x+map_r + 1):
					y3 = y2 % self.map_h
					x3 = x2 % self.map_w
					pos = (x3, y3)
					if pos in self.pos_obj:
						obj = self.pos_obj[pos]
						if obj.t == 3:
							l.append({'t':3, 'i':obj.i})
						else:
							l.append({'t':obj.t})
					else:
						l.append({'t':0})
				m.append(l)
			return m
		else:
			return []
	
SH = StateHolder()

class StreamComm(SocketConnection):
	def on_open(self, request):
		print "USER CONNECTED"
		try:
			self.userid = int(request.get_argument("userid"))
		except (TypeError, ValueError) as e:
			self.userid = None

		self.last_history_ts = None

		global SH
		self.state = SH
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
		self.push_map_update()
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
					self.push_usernames()
					self.push_userscores()
					self.push_map_update()
					self.push_user_history()
			else:
				msg = {
					'type': 'exception',
					'content': msg.body,
				}
				self.send(json.dumps(msg, use_decimal=True))

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

	def push_map_update(self):
		msg = {
			'type': 'map',
			'content': self.state.get_map_for(self.userid),
		}
		self.send(json.dumps(msg, use_decimal=True))

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

