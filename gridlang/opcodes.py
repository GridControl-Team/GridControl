from errors import GridLangPanicException
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

class POP_OPCODE(OPCODE):
	s = 'POP'
	@classmethod
	def run(cls, args, vm):
		vm.pop()

class SWAP_OPCODE(OPCODE):
	s = 'SWAP'
	@classmethod
	def run(cls, args, vm):
		a, b = vm.pop(2)
		vm.append(b)
		vm.append(a)

class DUP_OPCODE(OPCODE):
	s = 'DUP'
	@classmethod
	def run(cls, args, vm):
		a = vm.pop()
		vm.append(a)
		vm.append(a)

class PEEK_OPCODE(OPCODE):
	s = 'PEEK'
	@classmethod
	def run(cls, args, vm):
		a = vm.pop()
		val = vm.peek(a)
		vm.append(val)

class POKE_OPCODE(OPCODE):
	s = 'POKE'
	@classmethod
	def run(cls, args, vm):
		addr, val = vm.pop(2)
		vm.poke(addr, val)

class HERE_OPCODE(OPCODE):
	s = 'HERE'
	@classmethod
	def run(cls, args, vm):
		vm.append(vm.here())

class STORE_OPCODE(OPCODE):
	s = 'STORE'
	@classmethod
	def run(cls, args, vm):
		key = args[0]
		val = vm.pop()
		vm.store(key, val)

class GOTO_OPCODE(OPCODE):
	jump = True
	s = 'GOTO'
	@classmethod
	def run(cls, args, vm):
		val = vm.pop()
		jump = vm.map_goto_num(val)
		vm.exe.append(['JUMP', jump])

class TESTTGOTO_OPCODE(OPCODE):
	jump = True
	s = ['TESTTGOTO', 'IFTGOTO']
	@classmethod
	def run(cls, args, vm):
		val = vm.pop()
		if val > 0:
			jump = vm.map_goto_num(args[0])
		else:
			jump = vm.pos + 1
		vm.exe.append(['JUMP', jump])

class TESTFGOTO_OPCODE(OPCODE):
	jump = True
	s = ['TESTFGOTO', 'IFFGOTO']
	@classmethod
	def run(cls, args, vm):
		val = vm.pop()
		if val == 0:
			jump = vm.map_goto_num(args[0])
		else:
			jump = vm.pos + 1
		vm.exe.append(['JUMP', jump])

class PRINT_OPCODE(OPCODE):
	s = 'PRINT'
	@classmethod
	def run(cls, args, vm):
		val = vm.pop()
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
	s = ['MUL', 'MULTIPLY']
	o = operator.mul

class DIVIDE_OPCODE(OPERATOR_OPCODE):
	s = ['DIV', 'DIVIDE']
	o = operator.floordiv

class PLUS_OPCODE(OPERATOR_OPCODE):
	s = ['PLUS', 'ADD']
	o = operator.add

class MINUS_OPCODE(OPERATOR_OPCODE):
	s = ['MINUS', 'SUB']
	o = operator.sub

class MIN_OPCODE(OPERATOR_OPCODE):
	s = ['MIN', 'MINIMUM']
	o = min

class MAX_OPCODE(OPERATOR_OPCODE):
	s = ['MAX', 'MAXIMUM']
	o = max

class PANIC_OPCODE(OPCODE):
	s = 'PANIC'
	@classmethod
	def run(cls, args, vm):
		raise GridLangPanicException("PANIC CALLED")

class FFI_OPCODE(OPCODE):
	s = 'FFI'

	@classmethod
	def run(cls, args, vm):
		left, right = vm.pop(2)
		vm.call_ffi(left, right)
