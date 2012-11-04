import re

class TOKEN(object):
	def __init__(self, content):
		self.content = content
	
	@property
	def len(self):
		return len(self.content)

	def __repr__(self):
		return self.content

	def __unicode__(self):
		return self.content

	@classmethod
	def match(cls, s, pos):
		return cls.re.match(s, pos)

class TOKEN_WHITESPACE(TOKEN):
	r = r'[ \t\f\v]+'

class TOKEN_NEWLINE(TOKEN):
	r = r'[\n\r]+'

class TOKEN_OPENPARENS(TOKEN):
	r = r'\('

class TOKEN_CLOSEPARENS(TOKEN):
	r = r'\)'

class TOKEN_NUMBER(TOKEN):
	r = r'\d+'

class TOKEN_OPERATION(TOKEN):
	r = r'[\+\-\/\%\=]'

class TOKEN_LABEL(TOKEN):
	r = r'\w+'

class TOKEN_QUOTEDSTRING(TOKEN):
	r = r'"([^"\\]*(\\.[^"\\]*)*)"|\'([^\'\\]*(\\.[^\'\\]*)*)\''

TOKENS = [
	TOKEN_WHITESPACE,
	TOKEN_NEWLINE,
	TOKEN_OPENPARENS,
	TOKEN_CLOSEPARENS,
	TOKEN_NUMBER,
	TOKEN_OPERATION,
	TOKEN_QUOTEDSTRING,
	TOKEN_LABEL,
]

for tok in TOKENS:
	tok.re = re.compile(tok.r)

class GridLispLexer(object):
	def __init__(self, s):
		self.stream = s
		self.pos = 0
		self.row = 0
		self.col = 0
		self.len = len(self.stream)
	
	def next(self):
		for tok in TOKENS:
			m = tok.match(self.stream, self.pos)
			if m is not None:
				return tok(m.group(0))
		raise Exception("Invalid token at line {0}, character {1} \"{2}\"".format(self.row + 1, self.col + 1, self.stream[self.pos:self.pos+4]))
	
	def tokenize(self):
		while 1:
			if self.pos >= self.len:
				return
			n = self.next()
			self.pos += n.len
			self.col += n.len

			if not isinstance(n, TOKEN_WHITESPACE):
				yield n	

			if isinstance(n, TOKEN_NEWLINE):
				self.row += 1
				self.col = 0
