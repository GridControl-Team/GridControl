import operator

OPCODES = []

class _METAOPCODE(type):
	def __init__(cls, name, bases, dct):
		super(_METAOPCODE, cls).__init__(name, bases, dct)
		if object in bases or name=="OPERATOR_OPCODE":
			#this is base OPCODE class, let it go
			pass
		else:
			OPCODES.append(cls)

class _METAOPERATOR_OPCODE(_METAOPCODE):
	def __init__(cls, name, bases, dct):
		super(_METAOPERATOR_OPCODE, cls).__init__(name, bases, dct)
		def _run(cls, args, vm):
			left, right = vm.pop(2)
			vm.append(int(cls.o(left, right)))
		cls.run = classmethod(_run)

class OPCODE(object):
	__metaclass__ = _METAOPCODE
	jump = False
	@classmethod
	def match(cls, s):
		"""Does s match OPCODE label"""
		if hasattr(cls.s, '__iter__'):
			return s in cls.s
		return s == cls.s

	@classmethod
	def run(cls, args, vm):
		"""Stub function, please implement"""
		pass

class OPERATOR_OPCODE(OPCODE):
	__metaclass__ = _METAOPERATOR_OPCODE

class PUSH_OPCODE(OPCODE):
	s = 'PUSH'
	@classmethod
	def run(cls, args, vm):
		val = vm.eval(args[0])
		vm.append(val)

class STORE_OPCODE(OPCODE):
	s = 'STORE'
	@classmethod
	def run(cls, args, vm):
		key = args[0]
		val = vm.pop()
		vm.store(key, val)

class TESTTGOTO_OPCODE(OPCODE):
	jump = True
	s = 'TESTTGOTO'
	@classmethod
	def run(cls, args, vm):
		val = vm.pop()
		if val > 0:
			jump = vm.eval(args[0]) - 1
		else:
			jump = vm.pos + 1
		vm.exe.append(['JUMP', jump])

class TESTFGOTO_OPCODE(OPCODE):
	jump = True
	s = 'TESTFGOTO'
	@classmethod
	def run(cls, args, vm):
		val = vm.pop()
		if val == 0:
			jump = vm.eval(args[0]) - 1
		else:
			jump = vm.pos + 1
		vm.exe.append(['JUMP', jump])

class PRINT_OPCODE(OPCODE):
	s = 'PRINT'
	@classmethod
	def run(cls, args, vm):
		val = vm.data[-1]
		print val

class END_OPCODE(OPCODE):
	s = 'END'
	@classmethod
	def run(cls, args, vm):
		pass

class GREATER_OPCODE(OPERATOR_OPCODE):
	s = 'GREATER'
	o = operator.gt

class LESS_OPCODE(OPERATOR_OPCODE):
	s = 'LESS'
	o = operator.lt

class EQUAL_OPCODE(OPERATOR_OPCODE):
	s = 'EQUAL'
	o = operator.eq

class MULTIPLY_OPCODE(OPERATOR_OPCODE):
	s = 'MULTIPLY'
	o = operator.mul

class DIVIDE_OPCODE(OPERATOR_OPCODE):
	s = 'DIVIDE'
	o = operator.floordiv

class PLUS_OPCODE(OPERATOR_OPCODE):
	s = 'PLUS'
	o = operator.add

class MINUS_OPCODE(OPERATOR_OPCODE):
	s = 'MINUS'
	o = operator.sub

