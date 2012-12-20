class COMMAND(object):
	jump = False
	@classmethod
	def match(cls, s):
		if hasattr(cls.s, '__iter__'):
			return s in cls.s
		return s == cls.s

	@classmethod
	def run(cls, vm):
		pass

	@classmethod
	def eval(cls, i, vm):
		if type(i) in (int, float):
			return i
		else:
			return vm.reg.get(i)

class PUSH_COMMAND(COMMAND):
	s = 'PUSH'
	@classmethod
	def run(cls, args, vm):
		val = cls.eval(args[0], vm)
		vm.data.append(val)

class STORE_COMMAND(COMMAND):
	s = 'STORE'
	@classmethod
	def run(cls, args, vm):
		key = args[0]
		val = vm.data.pop()
		vm.reg[key] = val

class GREATER_COMMAND(COMMAND):
	s = 'GREATER'
	@classmethod
	def run(cls, args, vm):
		right = vm.data.pop()
		left = vm.data.pop()
		if (left > right):
			vm.data.append(1)
		else:
			vm.data.append(0)

class LESS_COMMAND(COMMAND):
	s = 'LESS'
	@classmethod
	def run(cls, args, vm):
		right = vm.data.pop()
		left = vm.data.pop()
		if (left < right):
			vm.data.append(1)
		else:
			vm.data.append(0)

class EQUAL_COMMAND(COMMAND):
	s = 'EQUAL'
	@classmethod
	def run(cls, args, vm):
		right = vm.data.pop()
		left = vm.data.pop()
		if (left == right):
			vm.data.append(1)
		else:
			vm.data.append(0)

class TESTTGOTO_COMMAND(COMMAND):
	jump = True
	s = 'TESTTGOTO'
	@classmethod
	def run(cls, args, vm):
		val = vm.data.pop()
		if val > 0:
			jump = cls.eval(args[0], vm) - 1
		else:
			jump = vm.pos + 1
		vm.exe.append(['JUMP', jump])

class TESTFGOTO_COMMAND(COMMAND):
	jump = True
	s = 'TESTFGOTO'
	@classmethod
	def run(cls, args, vm):
		val = vm.data.pop()
		if val == 0:
			jump = cls.eval(args[0], vm) - 1
		else:
			jump = vm.pos + 1
		vm.exe.append(['JUMP', jump])

class MULTIPLY_COMMAND(COMMAND):
	s = 'MULTIPLY'
	@classmethod
	def run(cls, args, vm):
		a = vm.data.pop()
		b = vm.data.pop()
		vm.data.append(a * b)

class DIVIDE_COMMAND(COMMAND):
	s = 'DIVIDE'
	@classmethod
	def run(cls, args, vm):
		a = vm.data.pop()
		b = vm.data.pop()
		vm.data.append(a / b)

class PLUS_COMMAND(COMMAND):
	s = 'PLUS'
	@classmethod
	def run(cls, args, vm):
		a = vm.data.pop()
		b = vm.data.pop()
		vm.data.append(b + a)

class MINUS_COMMAND(COMMAND):
	s = 'MINUS'
	@classmethod
	def run(cls, args, vm):
		a = vm.data.pop()
		b = vm.data.pop()
		vm.data.append(b - a)

class PRINT_COMMAND(COMMAND):
	s = 'PRINT'
	@classmethod
	def run(cls, args, vm):
		val = vm.data[-1]
		print val

class END_COMMAND(COMMAND):
	s = 'END'
	@classmethod
	def run(cls, args, vm):
		pass

COMMANDS = [
	PUSH_COMMAND,
	STORE_COMMAND,
	GREATER_COMMAND,
	LESS_COMMAND,
	EQUAL_COMMAND,
	TESTTGOTO_COMMAND,
	TESTFGOTO_COMMAND,
	MULTIPLY_COMMAND,
	DIVIDE_COMMAND,
	PLUS_COMMAND,
	MINUS_COMMAND,
	PRINT_COMMAND,
	END_COMMAND,
]

class GridLangVM(object):
	def __init__(self):
		self.data = []
		self.exe = []
		self.reg = {}
		self.pos = 0

	def set_stacks(self, data, registry, pos):
		self.data = data
		self.reg = registry
		self.pos = pos
	
	def set_code(self, code):
		self.code = code
	
	def next(self):
		p = self.pos
		newp = self.pos + 1
		line = self.code[p]
		cmd_s = line[0]
		args = line[1:]

		cmd = (CMD for CMD in COMMANDS if CMD.match(cmd_s)).next()
		if cmd is None:
			raise Exception("WTF")

		cmd.run(args, self)

		# if command does not involve jumping go to next line
		if cmd.jump == False:
			self.exe.append(["JUMP", newp])

		while 1:
			try:
				ecmd = self.exe.pop()
			except IndexError:
				break
			# assume we're just JUMP-ing now
			self.pos = ecmd[1]

		if self.pos >= len(self.code):
			return False
	
	def run(self):
		while 1:
			if self.next() == False:
				break
