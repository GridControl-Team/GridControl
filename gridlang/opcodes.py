from errors import GridLangPanicException
import operator
import random

OPCODES = []

class _METAOPCODE(type):
	def __init__(cls, name, bases, dct):
		super(_METAOPCODE, cls).__init__(name, bases, dct)
		if object in bases or name in ("OPERATOR_OPCODE", "OPERATION_OPCODE"):
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

class _METAOPERATION_OPCODE(_METAOPCODE):
	def __init__(cls, name, bases, dct):
		super(_METAOPERATION_OPCODE, cls).__init__(name, bases, dct)
		def _run(cls, args, vm):
			v = vm.pop()
			vm.append(int(cls.o(v)))
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
	
class OPERATION_OPCODE(OPCODE):
	__metaclass__ = _METAOPERATION_OPCODE

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

class POPN_OPCODE(OPCODE):
	s = 'POPN'
	@classmethod
	def run(cls, args, vm):
		v = vm.pop(t = int)
		vm.pop(v)

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
		val = vm.pop()
		addr = vm.pop(t=int)
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
		vm.append_exe(['JUMP', jump])

class TESTTGOTO_OPCODE(OPCODE):
	jump = True
	s = ['TESTTGOTO', 'IFTGOTO']
	@classmethod
	def run(cls, args, vm):
		val, arg = vm.pop(2, t = int)
		if val > 0:
			jump = vm.map_goto_num(arg)
		else:
			jump = vm.pos + 1
		vm.append_exe(['JUMP', jump])

class TESTFGOTO_OPCODE(OPCODE):
	jump = True
	s = ['TESTFGOTO', 'IFFGOTO']
	@classmethod
	def run(cls, args, vm):
		val, arg = vm.pop(2, t = int)
		if val <= 0:
			jump = vm.map_goto_num(arg)
		else:
			jump = vm.pos + 1
		vm.append_exe(['JUMP', jump])

class CALL_OPCODE(OPCODE):
	jump = True
	s = 'CALL'
	@classmethod
	def run(cls, args, vm):
		v = vm.pop()
		jump = vm.map_goto_num(v)
		ret = vm.pos + 1
		vm.append_exe(['JUMP', ret])
		vm.append_exe(['JUMP', jump])

class TESTFCALL_OPCODE(OPCODE):
	jump = True
	s = ['TESTFCALL', 'IFFCALL']
	@classmethod
	def run(cls, args, vm):
		val, arg = vm.pop(2)
		if val <= 0:
			jump = vm.map_goto_num(arg)
			ret = vm.pos + 1
			vm.append_exe(['JUMP', ret])
			vm.append_exe(['JUMP', jump])
		else:
			jump = vm.pos + 1
			vm.append_exe(['JUMP', jump])

class TESTTCALL_OPCODE(OPCODE):
	jump = True
	s = ['TESTTCALL', 'IFTCALL']
	@classmethod
	def run(cls, args, vm):
		val, arg = vm.pop(2)
		if val > 0:
			jump = vm.map_goto_num(args)
			ret = vm.pos + 1
			vm.append_exe(['JUMP', ret])
			vm.append_exe(['JUMP', jump])
		else:
			jump = vm.pos + 1
			vm.append_exe(['JUMP', jump])


class RETURN_OPCODE(OPCODE):
	jump = True
	s = 'RETURN'
	@classmethod
	def run(cls, args, vm):
		pass

class PRINT_OPCODE(OPCODE):
	s = 'PRINT'
	@classmethod
	def run(cls, args, vm):
		val = vm.pop()
		print val

class END_OPCODE(OPCODE):
	s = ['EXIT', 'END']
	@classmethod
	def run(cls, args, vm):
		vm.end()

class GREATER_OPCODE(OPERATOR_OPCODE):
	s = 'GREATER'
	o = operator.gt

class LESS_OPCODE(OPERATOR_OPCODE):
	s = 'LESS'
	o = operator.lt

class EQUAL_OPCODE(OPERATOR_OPCODE):
	s = 'EQUAL'
	o = operator.eq

class NOTEQUAL_OPCODE(OPERATOR_OPCODE):
	s = 'NEQUAL'
	o = operator.ne

class MULTIPLY_OPCODE(OPERATOR_OPCODE):
	s = ['MUL', 'MULTIPLY']
	o = operator.mul

class MODULO_OPCODE(OPERATOR_OPCODE):
	s = ['MODULO', 'MOD']
	o = operator.mod

class DIVIDE_OPCODE(OPERATOR_OPCODE):
	s = ['DIV', 'DIVIDE']
	o = operator.floordiv

class PLUS_OPCODE(OPERATOR_OPCODE):
	s = ['PLUS', 'ADD']
	o = operator.add

class MINUS_OPCODE(OPERATOR_OPCODE):
	s = ['MINUS', 'SUB']
	o = operator.sub

class ABS_OPCODE(OPERATION_OPCODE):
	s = ['ABS', 'ABSOLUTE']
	o = operator.abs

class NEG_OPCODE(OPERATION_OPCODE):
	s = ['NEG', 'NEGATIVE']
	o = operator.neg

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

class RAND_OPCODE(OPCODE):
	s = 'RAND'

	@classmethod
	def run(cls, args, vm):
		v = vm.pop(1, t = int)
		vm.append(random.randint(0, v))

class FFI_OPCODE(OPCODE):
	s = 'FFI'

	@classmethod
	def run(cls, args, vm):
		left, right = vm.pop(2)
		vm.call_ffi(left, right)

class CALLFF_OPCODE(OPCODE):
	s = 'CALLFF'

	@classmethod
	def run(cls, args, vm):
		v = vm.pop(1)
		args = vm.pop(v)
		vm.callff(*args)
