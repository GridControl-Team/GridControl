class GridLangException(Exception):
	pass

class GridLangParseException(GridLangException):
	def __init__(self, message, line_number=None, line_offset=1):
		self.msg = message
		if line_number:
			self.line_number = line_number + line_offset
		else:
			self.line_number = ":("

	def __str__(self):
		return "[{0}]: {1}".format(self.line_number, self.msg.title())

class GridLangExecutionException(GridLangException):
	pass

class GridLangExecutionEndException(GridLangExecutionException):
	pass

class GridLangPanicException(GridLangException):
	pass
