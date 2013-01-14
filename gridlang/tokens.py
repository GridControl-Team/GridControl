import re
from decimal import Decimal

TOKENS = []

for tok in TOKENS:
	tok.re = re.compile(tok.r)

class _METATOKEN(type):
	def __init__(cls, name, bases, dct):
		super(_METATOKEN, cls).__init__(name, bases, dct)
		if object in bases:
			# this is base TOKEN class, let it go
			pass
		else:
			TOKENS.append(cls)
			cls.re = re.compile(cls.r)

class TOKEN(object):
	__metaclass__ = _METATOKEN
	@classmethod
	def match(cls, s):
		return cls.re.match(s)

	@classmethod
	def emit(cls, i):
		return i

class TOKEN_COMMENT(TOKEN):
	r = r'^#.*$'
	
	def __init__(self):
		pass

	@classmethod
	def emit(cls, i):
		return cls()

class TOKEN_INT(TOKEN):
	r = r'^-?\d+$'
	@classmethod
	def emit(cls, i):
		return int(i)

class TOKEN_FLOAT(TOKEN):
	r = r'^-?\d+\.\d+$'
	@classmethod
	def emit(cls, i):
		return Decimal(i)

class TOKEN_CONSTANT(TOKEN):
	r = r'^@\w+$'

	def __init__(self, i):
		self.val = i

	@classmethod
	def emit(cls, i):
		return cls(i[1:])

class TOKEN_PUSHSUGAR(TOKEN):
	r = r'^<<$'

	def __init__(self):
		pass

	@classmethod
	def emit(cls, i):
		return cls()

class TOKEN_LABEL(TOKEN):
	r = r'^\w+$'

class TOKEN_JUNK(TOKEN):
	r = r'.*'

	def __init__(self, i):
		self.val = i

	@classmethod
	def emit(cls, i):
		return cls(i)
