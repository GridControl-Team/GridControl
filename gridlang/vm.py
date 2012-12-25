from opcodes import OPCODES

class GridLangVM(object):
	def __init__(self):
		self.data = []
		self.exe = []
		self.reg = {}
		self.pos = 0
		self.debug = False
	
	def trace(self, *args):
		if self.debug:
			print " >> ",
			for arg in args:
				print arg,
			print ""

	def set_stacks(self, data, registry, pos):
		self.data = data
		self.reg = registry
		self.pos = pos
	
	def set_code(self, code):
		self.code = code
	
	def pop(self, n = 1):
		ret = []
		try:
			for i in xrange(n):
				ret.append(self.data.pop())
		except IndexError:
			raise Exception("No more stack")
		if n == 1:
			ret = ret[0]
		self.trace("Pop", n, ret, self.data)
		return ret

	def append(self, *args):
		self.data.extend(args)
		self.trace("Appending", args, self.data)
	
	def eval(self, i):
		if type(i) in (int, float):
			return i
		else:
			return self.get(i)

	def store(self, key, val):
		self.reg[key] = val
		self.trace("Storing", key, val, self.reg)
	
	def get(self, key):
		return self.reg.get(key)
	
	def next(self):
		p = self.pos
		newp = self.pos + 1
		line = self.code[p]
		cmd_s = line[0]
		args = line[1:]

		try:
			cmd = (CMD for CMD in OPCODES if CMD.match(cmd_s)).next()
		except StopIteration as e:
			raise Exception("UNKNOWN OPCODE {0}".format(cmd_s))
		if cmd is None:
			raise Exception("WTF")

		self.trace("Executing", cmd, args)
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
