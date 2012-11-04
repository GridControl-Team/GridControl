from parser import GridLispParser
from vm import GridLisp

""" Many thanks to http://norvig.com/lispy.html """

if __name__ == "__main__":
	with open("code.gridlisp") as fh:
		code = fh.read()
	c = GridLispParser.parse(code)
	GridLisp.execute(c)
