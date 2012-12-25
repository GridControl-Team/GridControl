from tokens import TOKENS
from opcodes import PUSH_OPCODE

class GridLangCode(object):
	def __init__(self):
		self.raw = ""
		self.lines = []
		self.mapping = {}
	
	def get_line(self, ln):
		return self.lines[ln]

	def get_goto_line(self, src_ln):
		return self.mapping.get(src_ln)

	def freeze(self):
		ret = {
			'raw': str(self.raw),
			'lines': list(self.lines),
			'mapping': dict(self.mapping),
		}
		return ret

	def thaw(self, data):
		self.raw = str(data['raw'])
		self.lines = list(data['lines'])
		self.mapping = dict(data['mapping'])

class GridLangParser(object):
	@classmethod
	def parse(cls, code):
		glc = GridLangCode()
		glc.raw = code
		lines = code.split("\n")
		for src_ln, line in enumerate(lines):
			ln = len(glc.lines)
			line = line.strip().upper()
			parts_raw = line.split()

			parts = []

			if "<<" in parts_raw:
				i = parts_raw.index("<<")
				parts_raw, parts_push = parts_raw[:i], parts_raw[i+1:]

				for part in parts_push:
					try:
						matched = (tok.emit(part) for tok in TOKENS if tok.match(part) is not None).next()
					except IndexError:
						raise Exception("Invalid TOKEN")
					glc.lines.append([PUSH_OPCODE.s, matched])

			for part in parts_raw:
				try:
					matched = (tok.emit(part) for tok in TOKENS if tok.match(part) is not None).next()
				except IndexError:
					raise Exception("Invalid TOKEN")
				parts.append(matched)

			if len(parts):
				glc.lines.append(parts)
				glc.mapping[src_ln] = ln
		return glc

