from tokens import TOKENS, CONSTANT
from opcodes import PUSH_OPCODE
from errors import *

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
		#json trounces the integer keys, so we have to fix them here
		self.mapping = dict((int(k), int(v)) for k,v in data['mapping'].iteritems())

class GridLangParser(object):

	@classmethod
	def match_token(cls, part):
		try:
			matched = (tok.emit(part) for tok in TOKENS if tok.match(part) is not None).next()
		except (IndexError, StopIteration) as e:
			raise GridLangParseException("Invalid TOKEN: {0}".format(part))
		return matched

	@classmethod
	def parse(cls, code, constants=None):
		glc = GridLangCode()
		glc.raw = code
		lines = code.split("\n")

		if constants is None:
			constants = {}
		else:
			constants = dict(constants)

		for src_ln, line in enumerate(lines):
			ln = len(glc.lines)
			line = line.strip().upper()
			if line.startswith("#"):
				# this was a comment
				line = ""
			parts_raw = line.split()

			parts = []

			if "<<" in parts_raw:
				i = parts_raw.index("<<")
				parts_raw, parts_push = parts_raw[:i], parts_raw[i+1:]

				for part in parts_push:
					matched = cls.match_token(part)
					glc.lines.append([PUSH_OPCODE.s, matched])

			for part in parts_raw:
				matched = cls.match_token(part)
				parts.append(matched)

			if len(parts):
				if type(parts[0]) == CONSTANT:
					# handle CONSTANTs
					if len(parts) == 1:
						v = parts[0].val
						if v not in constants:
							constants[v] = src_ln + 1
						else:
							raise GridLangParseException("LABEL {0} ALREADY DEFINED".format(v))
					else:
						raise GridLangParseException("PARSE ERROR: NO CODE ALLOWED AFTER CONSTANT")
				else:
					glc.lines.append(parts)
					glc.mapping[src_ln] = ln

		# postprocess CONSTANTs
		for line in glc.lines:
			for i, part in enumerate(line):
				if type(part) == CONSTANT:
					v = constants.get(part.val)
					if v is not None:
						line[i] = v
					else:
						raise GridLangParseException("NO SUCH CONSTANT {0}".format(part.val))

		# backfill mapping for empty lines
		# fixes bad GOTOs
		src_lns = len(lines)
		p = src_lns
		for src_ln in reversed(xrange(src_lns)):
			if src_ln not in glc.mapping:
				glc.mapping[src_ln] = p
			else:
				p = glc.mapping[src_ln]

		return glc

