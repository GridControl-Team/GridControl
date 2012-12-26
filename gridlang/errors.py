class GridLangException(Exception):
	pass

class GridLangParseException(GridLangException):
	pass

class GridLangExecutionException(GridLangException):
	pass

class GridLangPanicException(GridLangException):
	pass
