#!/usr/bin/env python
from parser import GridLangParser
from vm import GridLangVM
from errors import GridLangParseException
import sys

if __name__ == "__main__":
	if len(sys.argv) > 1:
		fn = sys.argv[1]
	else:
		sys.exit("What file should I operate on?")

	with open(fn) as fh:
		code = fh.read()
		try:
			c = GridLangParser.parse(code)
		except GridLangParseException as e:
			sys.exit(e)

	vm = GridLangVM()
	vm.set_code(c)
	vm.run()
