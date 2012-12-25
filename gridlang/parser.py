from tokens import TOKENS

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

