from tornadio2 import TornadioRouter, SocketConnection
import tornadoredis
import json

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
		self.c = 4
		self.redis.hgetall("user_usernames", self.on_get_usernames)
		self.redis.get("user_attr", self.on_get_userattr)
		self.redis.get("users_data", self.on_get_users)
		self.redis.get("resource_map", self.on_get_map)
	
	def on_subscribed(self, smt):
		self.pubsub.listen(self.on_redis)

	def on_redis(self, msg):
		if msg.kind == 'message':
			if msg.channel == 'global_tick' and msg.body == 'tick':
				if self.c != 0:
					return
				self.c = 4
				self.redis.hgetall("user_usernames", self.on_get_usernames)
				self.redis.get("user_attr", self.on_get_userattr)
				self.redis.get("users_data", self.on_get_users)
				self.redis.get("resource_map", self.on_get_map)

	def on_get_usernames(self, val):
		self.usernames = val
		self.next()
	
	def on_get_userattr(self, val):
		self.userattr = json.loads(val)
		print self.userattr
		self.userscores = {}
		for k, v in self.userattr.iteritems():
			if k.endswith(":resources"):
				uid = k.split(":")[0]
				self.userscores[uid] = v
		self.next()

	def on_get_map(self, val):
		self.map_data = json.loads(val)
		self.map_h = len(self.map_data)
		self.map_w = len(self.map_data[0])
		self.next()

	def on_get_users(self, val):
		if val is not None:
			self.user_pos = json.loads(val)
			self.pos_user = dict((tuple(v), k) for k, v in self.user_pos.iteritems())
		else:
			self.user_pos = {}
			self.pos_user = {}
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
					l.append(self.map_data[y3][x3])
				m.append(l)
			return m
		else:
			return []
	
	def get_users_for(self, userid):
		uid = str(userid)
		map_r = 5
		if uid in self.user_pos:
			x, y = self.user_pos[uid]
			ret = {}
			for y2 in xrange(y-map_r, y+map_r + 1):
				for x2 in xrange(x-map_r, x+map_r + 1):
					coord = (x2 % self.map_w, y2 % self.map_h)
					if coord in self.pos_user:
						user = self.pos_user[coord]
						ret[user] = [x2 - x + map_r, y2 - y + map_r]
			return ret
		else:
			return {}


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
		self.push_user_update()
		self.push_user_history()
	
	def on_subscribed(self, smt):
		self.pubsub.listen(self.on_redis)

	def on_redis(self, msg):
		if msg.kind == 'message':
			if msg.channel == 'global_tick':
				if msg.body == 'tock':
					self.push_usernames()
					self.push_userscores()
					self.push_map_update()
					self.push_user_update()
					self.push_user_history()
			else:
				msg = {
					'type': 'exception',
					'content': msg.body,
				}
				self.send(json.dumps(msg))

	def push_usernames(self):
		msg = {
			'type': 'username',
			'content': self.state.usernames,
		}
		self.send(json.dumps(msg))

	def push_userscores(self):
		msg = {
			'type': 'scores',
			'content': self.state.userscores,
		}
		self.send(json.dumps(msg))

	def push_map_update(self):
		msg = {
			'type': 'map',
			'content': self.state.get_map_for(self.userid),
		}
		self.send(json.dumps(msg))

	def push_user_update(self):
		msg = {
			'type': 'users',
			'content': self.state.get_users_for(self.userid),
		}
		self.send(json.dumps(msg))

	def push_user_history(self):
		self.redis.lrange("user_history_{0}".format(self.userid), 0, 15, self.on_user_history)
	
	def on_user_history(self, val):
		msg = {
			'type': 'history',
			'content': val,
		}
		self.send(json.dumps(msg))

