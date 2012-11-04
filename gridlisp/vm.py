from lexer import*

class Construct(object):
	@classmethod
	def is_a(cls, i):
		if isinstance(i, cls.head):
			if hasattr(cls, "match"):
				return i.content == cls.match
			return True
		return False

class Method(Construct):
	def __init__(self, val, args):
		if hasattr(self, "num_args") and len(args) != self.num_args:
			print args
			raise Exception("Wrong num args for {0}, got {1} expected {2}".format(str(self), len(args), self.num_args))
		self.val = val
		self.args = args

class Value(Construct):
	def __init__(self, val):
		self.val = val

class NumberValue(Value):
	head = TOKEN_NUMBER

	def ex(self):
		return int(self.val.content)

class TrueValue(Value):
	head = TOKEN_LABEL
	match = "true"
	content = True
	
	def ex(self):
		return True

class FalseValue(Value):
	head = TOKEN_LABEL
	match = "false"
	content = False

	def ex(self):
		return False

class StringValue(Value):
	head = TOKEN_QUOTEDSTRING

	def ex(self):
		return self.val

class IfMethod(Method):
	head = TOKEN_LABEL
	match = "if"
	num_args = 3

	def ex(self):
		if self.args[0].ex():
			self.args[1].ex()
		else:
			self.args[2].ex()

class EqMethod(Method):
	head = TOKEN_LABEL
	match = "eq"
	num_args = 2

	def ex(self):
		if self.args[0].ex() == self.args[1].ex():
			return True
		else:
			return False

class PrintMethod(Method):
	head = TOKEN_LABEL
	match = "print"
	num_args = 1

	def ex(self):
		print self.args[0].ex()

class OperationMethod(Method):
	head = TOKEN_OPERATION

	def ex(self):
		if self.val.content == '+':
			return self.args[0].ex() + self.args[1].ex()
		elif self.val.content == '-':
			return self.args[0].ex() - self.args[1].ex()
		elif self.val.content == '/':
			return self.args[0].ex() / self.args[1].ex()
		elif self.val.content == '%':
			return self.args[0].ex() % self.args[1].ex()
	
	
CONSTRUCTS = [
	TrueValue,
	FalseValue,
	NumberValue,
	StringValue,
	EqMethod,
	IfMethod,
	PrintMethod,
	OperationMethod,
]

class GridLisp(object):
	@staticmethod
	def execute(c):
		for l in c:
			l.ex()
