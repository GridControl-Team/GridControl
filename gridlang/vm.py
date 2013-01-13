from opcodes import OPCODES
from errors import *

class GridLangVM(object):
	def __init__(self):
		self.data = []
		self.exe = []
		self.reg = {}
		self.flags = set()
		self.pos = 0
		self.steps = 0
		self.data_limit = None
		self.exe_limit = None
		self.reg_limit = None
		self.debug = False
		self.capture_exception = False

		self.code = None
		self.ffi = None
	
	def trace(self, *args):
		if self.debug:
			print " >> ",
			for arg in args:
				print arg,
			print ""
	
	def call_ffi(self, *args):
		if self.ffi is not None:
			ret = self.ffi(self, args)
			if ret is not None:
				self.append(ret)
	
	def callff(self, *args):
		if self.ffi is not None:
			ret = self.ffi(self, args)
			if ret is not None:
				self.append(ret)
	
	def freeze(self):
		"""Return a copy of all pertinent data structures necessary
		to store the executable state of this vm"""
		ret = {
			'data': list(self.data),
			'exe': list(self.exe),
			'reg': dict(self.reg),
			'pos': self.pos,
			'steps': self.steps,
			'flags': list(self.flags),
		}
		return ret

	def thaw(self, data):
		"""Reload a previously frozen state of a vm"""
		self.data = list(data.get('data', []))
		self.exe = list(data.get('exe', []))
		self.reg = dict(data.get('reg', {}))
		self.pos = data.get('pos', 0)
		self.steps = data.get('steps', 0)
		self.flags = set(data.get('flags', []))

	def set_code(self, code):
		"""Attach opcodes to this vm"""
		self.code = code
	
	###### VM data access methods ########
	# These methods are used in OPCODE run method to access data, use these
	# methods because exception handling is a good idea
	def pop(self, n = 1, t = None):
		"""Pop n items off of stack"""
		i = len(self.data) - n
		if i < 0:
			raise GridLangExecutionException("Stack empty")
		self.data, ret = self.data[:i], self.data[i:]
		if t is not None:
			if any(type(v) != t for v in ret):
				raise GridLangExecutionException("Type error")
		if n == 1:
			ret = ret[0]
		self.trace("Pop", n, ret, self.data)
		return ret

	def append(self, *args):
		"""Push items onto stack"""
		if self.data_limit is not None:
			if (len(self.data) + len(args)) > self.data_limit:
				raise GridLangExecutionException("Data Stack exhausted")
		self.data.extend(args)
		self.trace("Appending", args, self.data)

	def append_exe(self, *args):
		"""Push items onto stack"""
		if self.exe_limit is not None:
			if (len(self.exe) + len(args)) > self.exe_limit:
				raise GridLangExecutionException("Execution Stack exhausted")
		self.exe.extend(args)
		self.trace("Appending", args, self.exe)
	
	def peek(self, addr):
		"""Look at addr in stack"""
		try:
			return self.data[addr]
		except IndexError:
			raise GridLangExecutionException("Invalid Stack Access")

	def poke(self, addr, val):
		"""Look at addr in stack"""
		try:
			self.data[addr] = val
		except IndexError:
			raise GridLangExecutionException("Invalid Stack Access")
	
	def here(self):
		"""Get current address in stack"""
		return len(self.data)
	
	def eval(self, i):
		"""If i is not a scalar resolve it out of the registry"""
		if type(i) in (int, float):
			return i
		else:
			return self.get(i)

	def store(self, key, val):
		"""Store value in the registry under key"""
		if self.reg_limit is not None:
			if key not in self.reg:
				if len(self.reg) + 1 > self.reg_limit:
					raise GridLangExecutionException("Registry exhausted")
		self.reg[key] = val
		self.trace("Storing", key, val, self.reg)
	
	def get(self, key):
		"""Get an item out of the registry"""
		return self.reg.get(key)

	def map_goto_num(self, i):
		val = self.eval(i) - 1
		return self.code.get_goto_line(val)

	def end(self):
		"""Stop execution, do this by
		jumping past the end of code"""
		self.pos = len(self.code.lines)

	###### VM Execution methods ##############
	def __run_step(self):
		p = self.pos
		newp = p + 1
		try:
			line = self.code.get_line(p)
		except GridLangExecutionEndException:
			return False
		cmd_s = line[0]
		args = line[1:]

		try:
			cmd = (CMD for CMD in OPCODES if CMD.match(cmd_s)).next()
		except StopIteration as e:
			raise GridLangExecutionException("UNKNOWN OPCODE {0}".format(cmd_s))
		if cmd is None:
			raise GridLangExecutionException("WTF")

		self.trace("Executing", cmd, args)
		cmd.run(args, self)

		# if command does not involve jumping go to next line
		if cmd.jump == False:
			self.pos = max(self.pos, newp)
		else:
			try:
				ecmd = self.exe.pop()
			except IndexError:
				raise GridLangExecutionException("EXEC STACK EXHAUSTED")
			# assume we're just JUMP-ing now
			self.pos = ecmd[1]

		if self.pos >= len(self.code.lines):
			# ran off the bottom of the code
			return False
	
	def __run_forever(self):
		while 1:
			if self.__run_step() == False:
				break

	def __run_steps(self, n):
		self.steps = self.steps + n
		while 1:
			if self.__run_step() == False:
				return True
			self.steps = self.steps - 1
			if self.steps < 0:
				self.trace("Freezing")
				return False
	
	def run(self, steps = None):
		try:
			if steps is None:
				return self.__run_forever()
			else:
				return self.__run_steps(steps)
		except GridLangException as e:
			self.output_traceback(e)
			raise e

	def output_traceback(self, e = None):
		msg = "Stack: {0}\nExecStack: {1}\nRegistry:{2}\n".format(str(self.data), str(self.exe), str(self.reg))

		minln = max(self.pos - 5, 0)
		maxln = self.pos + 5
		for i, line in enumerate(self.code.lines[minln:maxln]):
			ln = i + minln
			msg = msg + "{0} : {1}\n".format("*" if (ln == self.pos) else ln, line)

		if self.capture_exception:
			if e is not None:
				e.traceback = msg
		else:
			print msg
