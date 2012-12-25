from parser import GridLangParser
from vm import GridLangVM
import sys

if __name__ == "__main__":
	if len(sys.argv) > 1:
		fn = sys.argv[1]
	else:
		fn = "code.gridlang"

	with open(fn) as fh:
		code = fh.read()
	c = GridLangParser.parse(code)

	vm = None
	data = None

	while 1:
		if vm is not None:
			data = vm.freeze()
		vm = GridLangVM()
		vm.set_code(c)
		if data is not None:
			vm.thaw(data)
		if vm.run(10):
			break
		
