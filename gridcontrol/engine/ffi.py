
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

	def __init__(self, data):
		self.game_data = data

	def call_ffi(self, vm, args):
		cmd = args[0]
		val = args[1]
		if cmd == self.CONSTANTS.get('LOOK'):
			print "LOOKING"
			return 0
		elif cmd == self.CONSTANTS.get('PULL'):
			print "PULLING"
			return 1
		elif cmd == self.CONSTANTS.get('MOVE'):
			print "MOVING"
			return 1
