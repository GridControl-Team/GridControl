from gridlang.errors import GridLangException

class GridControlFFI(object):
	CONSTANTS = {
		'NORTH': 0,
		'EAST': 1,
		'SOUTH': 2,
		'WEST': 3,

		'LOOK': 1,
		'PULL': 2,
		'MOVE': 3,
		'SCAN': 4,

		'CELL_EMPTY': 0,
		'CELL_RESOURCE': 1,
		'CELL_ROCK': 2,
		'CELL_ROBOT': 10,
	}

	def __init__(self, user_id, gamestate):
		self.user_id = user_id
		self.gamestate = gamestate

	def call_ffi(self, vm, args):
		cmd = args[0]
		val = args[1:]

		try:
			cmd_s = [c for c in ['LOOK', 'PULL', 'MOVE', 'SCAN'] if self.CONSTANTS[c]==cmd][0]
		except IndexError as e:
			raise GridLangException("No such command for FFI: {0}".format(cmd))

		if cmd_s == 'SCAN':
			val_s = str(val)
		else:
			val = val[0]
			try:
				val_s = [c for c in ['NORTH', 'SOUTH', 'EAST', 'WEST'] if self.CONSTANTS[c]==val][0]
			except IndexError as e:
				raise GridLangException("No such value for FFI SCAN: {0}".format(val))

		self.gamestate.user_history(self.user_id, cmd_s, val_s)

		if cmd == self.CONSTANTS.get('LOOK'):
			return self.gamestate.user_look(self.user_id, val)
		elif cmd == self.CONSTANTS.get('PULL'):
			ret = self.gamestate.user_pull(self.user_id, val)
			if ret == 1:
				self.gamestate.add_score(self.user_id)
			vm.steps = 0
			return ret
		elif cmd == self.CONSTANTS.get('MOVE'):
			ret = self.gamestate.move_user(self.user_id, val)
			vm.steps = 0
			return ret
		elif cmd == self.CONSTANTS.get('SCAN'):
			ret = self.gamestate.user_scan(self.user_id, val)
			return ret
