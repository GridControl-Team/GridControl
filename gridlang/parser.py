import re

class TOKEN(object):
	@classmethod
	def match(cls, s):
		return cls.re.match(s)

	@classmethod
	def emit(cls, i):
		return i

class TOKEN_INT(TOKEN):
	r = r'^\d+$'
	@classmethod
	def emit(cls, i):
		return int(i)

class TOKEN_FLOAT(TOKEN):
	r = r'^\d+\.\d+$'
	@classmethod
	def emit(cls, i):
		return float(i)

class TOKEN_LABEL(TOKEN):
	r = r'^\w+$'

TOKENS = [
	TOKEN_INT,
	TOKEN_FLOAT,
	TOKEN_LABEL,
]

for tok in TOKENS:
	tok.re = re.compile(tok.r)

class GridLangParser(object):
	@classmethod
	def parse(cls, code):
		ret = []
		lines = code.split("\n")
		for line in lines:
			line = line.strip().upper()
			parts_raw = line.split()
			parts = []
			for part in parts_raw:
				try:
					matched = (tok.emit(part) for tok in TOKENS if tok.match(part) is not None).next()
				except IndexError:
					raise Exception("Invalid TOKEN")
				parts.append(matched)
			if len(parts):
				ret.append(parts)
		return ret

