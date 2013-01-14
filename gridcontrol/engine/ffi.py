from gridlang.errors import GridLangException

LOCATIONS = ['HERE', 'NORTH', 'EAST', 'SOUTH', 'WEST']

ACTIONS = ['LOOK', 'PULL', 'MOVE', 'SCAN', 'PUSH', 'LOCATE', 'IDENTIFY', 'INSPECT', 'PUNCH', 'CHARGEUP', 'PEWPEW', 'SELFDESTRUCT']

IDENTIFICATION = ['CELL_EMPTY', 'CELL_RESOURCE', 'CELL_ROCK', 'CELL_ROBOT']

ATTRS = ['CHARGE', 'RESOURCES', 'SHIELD', 'CALLSIGN', 'POINTS', 'STATUS']

STATUS = ['OK', 'DEAD', 'STUNNED']

CONSTANTS = {}
for C in [LOCATIONS, ACTIONS, IDENTIFICATION, ATTRS, STATUS]:
	for i, s in enumerate(C):
		CONSTANTS[s] = i
	
def pluck(s, LST):
	try:
		return [c for c in LST if CONSTANTS[c] == s][0]
	except IndexError as e:
		raise GridLangException("Invalid FFI parameter: {0}".format(s))


class GridControlFFI(object):

	def __init__(self, user_id, gamestate):
		self.user_id = user_id
		self.gamestate = gamestate

	def call_ffi(self, vm, args):
		cmd = args[0]
		val = args[1:]
		ret = None

		cmd_s = pluck(cmd, ACTIONS)
		args_s = None

		if cmd_s == 'SCAN': # scan operations
			if len(val) < 2:
				raise GridLangException("Scan needs two arguments")
			newargs = val[:2]
		elif cmd_s in ('SHIELD', 'CHARGE'): # one argument commands
			if len(val) < 1:
				raise GridLangException("{0} needs 1 argument".format(cmd_s))
			newargs = val[:1]
			args_s = str(val[0])
		elif cmd_s in ('INSPECT',): # direction, attr command
			if len(val) < 2:
				raise GridLangException("Inspect needs two arguments")
			dir_s = pluck(val[0], LOCATIONS)
			attr = pluck(val[1], ATTRS)
			newargs = val[:2]
		elif cmd_s == 'LOCATE':
			newargs = []
		elif cmd_s ==	'SELFDESTRUCT':
			newargs = []
			args_s = "BOOM!"
		else: # takes direction argument
			if len(val) < 1:
				raise GridLangException("{0} needs 1 argument".format(cmd_s))
			newargs = val[:1]
			if cmd_s in ('PULL', 'MOVE', 'PUSH', 'PUNCH'):
				args_s = pluck(val[0], LOCATIONS)

		f = getattr(self.gamestate, "do_user_{0}".format(cmd_s.lower()))
		ret = f(self.user_id, *newargs)

		if args_s is not None:
			self.gamestate.user_history(self.user_id, cmd_s, args_s, ret)

		if cmd_s in ('PULL', 'MOVE', 'PUSH', 'CHARGEUP', 'SELFDESTRUCT', 'PUNCH'):
			vm.steps = 0

		return ret

