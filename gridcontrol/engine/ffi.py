
class GridControlFFI(object):
	CONSTANTS = {
		'NORTH': 0,
		'EAST': 1,
		'SOUTH': 2,
		'WEST': 3,

		'LOOK': 1,
		'PULL': 2,
		'MOVE': 3,
	}

	def __init__(self, user_id, gamestate):
		self.user_id = user_id
		self.gamestate = gamestate

	def call_ffi(self, vm, args):
		cmd = args[0]
		val = args[1]
		if cmd == self.CONSTANTS.get('LOOK'):
			return self.gamestate.user_look(self.user_id, val)
		elif cmd == self.CONSTANTS.get('PULL'):
			ret = self.gamestate.user_pull(self.user_id, val)
			if ret == 1:
				self.gamestate.add_score(self.user_id)
			vm.steps = 0
			return 1
		elif cmd == self.CONSTANTS.get('MOVE'):
			self.gamestate.move_user(self.user_id, val)
			vm.steps = 0
			return 1
