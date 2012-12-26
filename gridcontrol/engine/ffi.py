
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

	@classmethod
	def call_ffi(cls, vm, args):
		pass
