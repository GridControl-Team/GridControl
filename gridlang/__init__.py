from parser import GridLangParser
from vm import GridLangVM

if __name__ == "__main__":
	with open("code.gridlang") as fh:
		code = fh.read()
	c = GridLangParser.parse(code)

	vm = None
	data = None

	while 1:
		if vm is not None:
			data = vm.freeze_vm()
		vm = GridLangVM()
		vm.set_code(c)
		if data is not None:
			vm.thaw_vm(data)
		if vm.run(10):
			break
		
