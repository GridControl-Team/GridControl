from parser import GridLangParser
from vm import GridLangVM
import sys

if __name__ == "__main__":
	if len(sys.argv) > 1:
		fn = sys.argv[1]
	else:
		print "What file should I operate on?"
		exit()

	with open(fn) as fh:
		code = fh.read()
	c = GridLangParser.parse(code)

	vm = GridLangVM()
	vm.set_code(c)
	vm.run()
