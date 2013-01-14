from tokens import TOKENS, TOKEN_CONSTANT, TOKEN_PUSHSUGAR, TOKEN_JUNK, TOKEN_COMMENT
from opcodes import PUSH_OPCODE
from errors import *

class GridLangCode(object):
	def __init__(self):
		self.raw = ""
		self.lines = []
		self.mapping = {}
		self.reverse_mapping = []
	
	def get_line(self, ln):
		try:
			return self.lines[ln]
		except IndexError as e:
			raise GridLangExecutionEndException()

	def get_goto_line(self, src_ln):
		return self.mapping.get(src_ln)

	def freeze(self):
		ret = {
			'raw': str(self.raw),
			'lines': list(self.lines),
			'mapping': dict(self.mapping),
			'reverse_mapping': list(self.reverse_mapping)
		}
		return ret

	def thaw(self, data):
		self.raw = str(data['raw'])
		self.lines = list(data['lines'])
		#json trounces the integer keys, so we have to fix them here
		self.mapping = dict((int(k), int(v)) for k,v in data['mapping'].iteritems())
		self.reverse_mapping = list(data['reverse_mapping'])
	
	def print_code(self):
		print self.raw
		maxln = len(self.lines)
		maxdg = len(str(maxln))

		for ln, line in enumerate(self.lines):
			print str(ln).rjust(maxdg),
			print str(self.get_goto_line(ln)).rjust(maxdg),
			print line

class GridLangParser(object):

	@classmethod
	def match_token(cls, part):
		try:
			matched = (tok.emit(part) for tok in TOKENS if tok.match(part) is not None).next()
		except (IndexError, StopIteration) as e:
			raise GridLangParseException("Invalid TOKEN: {0}".format(part))
		return matched

	@classmethod
	def parse(cls, code, constants=None, line_limit=None, const_limit=None):
		glc = GridLangCode()
		glc.raw = code
		lines = code.split("\n")

		if line_limit is not None:
			if len(lines) > line_limit:
				raise GridLangParseException("Too many lines")

		if constants is None:
			constants = {}
		else:
			constants = dict(constants)
			if const_limit is not None:
				# don't count predefined consts in limit
				const_limit = const_limit + len(constants)

		for src_ln, line in enumerate(lines):
			ln = len(glc.lines)
			line = line.strip().upper()

			parts_raw = line.split()

			parts = []
			parts_push = []
			push_sugar = False

			for part in parts_raw:
				matched = cls.match_token(part)
				if matched is not None:
					if isinstance(matched, TOKEN_COMMENT):
						# at first sight of TOKEN_COMMENT, discard
						# all subsequent tokens
						break
					if isinstance(matched, TOKEN_JUNK):
						raise GridLangParseException("Untokenizable entity: {0}".format(matched.val))
					elif isinstance(matched, TOKEN_PUSHSUGAR):
						if push_sugar:
							raise GridLangParseException("Cannot have two TOKEN_PUSHSUGAR on one line")
						push_sugar = True
					elif push_sugar:
						parts_push.append(matched)
					else:
						parts.append(matched)

			for matched in parts_push:
				glc.lines.append([PUSH_OPCODE.s, matched])
				glc.reverse_mapping.append(src_ln)

			if len(parts):
				if isinstance(parts[0], TOKEN_CONSTANT):
					# handle CONSTANTs
					if len(parts) == 1:
						c = parts[0].val
						if c not in constants:
							constants[c] = src_ln + 1
						else:
							raise GridLangParseException("Label {0} already defined".format(c), src_ln)
					elif len(parts) == 2 and type(parts[1]) in (int, float):
						c = parts[0].val
						if c not in constants:
							constants[c] = parts[1]
						else:
							raise GridLangParseException("Label {0} already defined".format(c), src_ln)
					else:
						raise GridLangParseException("No code allowed after constant", src_ln)
				else:
					glc.lines.append(parts)
					glc.mapping[src_ln] = ln
					glc.reverse_mapping.append(src_ln)

				if const_limit is not None:
					if len(constants) > const_limit:
						raise GridLangParseException("Too many constants")

		# postprocess CONSTANTs
		for line in glc.lines:
			for i, part in enumerate(line):
				if isinstance(part, TOKEN_CONSTANT):
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

