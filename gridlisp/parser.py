from lexer import *
from vm import *

class GridLispParser(object):

	@staticmethod
	def match_construct(i):
		if isinstance(i, Construct):
			return i
		for c in CONSTRUCTS:
			if c.is_a(i):
				return c
		raise Exception("Missing construct " + i.content)

	@staticmethod
	def to_ast(i):
		if hasattr(i, "__iter__"):
			first = i[0]
			if isinstance(first, Construct):
				return first
			con = GridLispParser.match_construct(first)
			return con(first, [GridLispParser.to_ast(_i) for _i in i[1:]])
		else:
			if isinstance(i, Construct):
				return i
			con = GridLispParser.match_construct(i)
			return con(i)

	@staticmethod
	def consume(tokens, _L):
		while 1:
			try:
				token = tokens.next()
			except StopIteration:
				return GridLispParser.to_ast(_L)
			if isinstance(token, TOKEN_OPENPARENS):
				L = []
				GridLispParser.consume(tokens, L)
				_L.append(GridLispParser.to_ast(L))
			elif isinstance(token, TOKEN_CLOSEPARENS):
				return GridLispParser.to_ast(_L)
			elif isinstance(token, (TOKEN_WHITESPACE, TOKEN_NEWLINE)):
				pass
			else:
				_L.append(token)

	@staticmethod
	def parse(code):
		lexer = GridLispLexer(code)
		tokens = lexer.tokenize()
		L = []
		GridLispParser.consume(tokens, L)
		return L
