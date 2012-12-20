from parser import GridLangParser
from vm import GridLangVM

if __name__ == "__main__":
	with open("code.gridlang") as fh:
		code = fh.read()
	c = GridLangParser.parse(code)

	vm = GridLangVM()
	vm.set_stacks([], {}, 0)
	vm.set_code(c)

	vm.run()
