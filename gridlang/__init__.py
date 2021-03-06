from parser import GridLangParser
from vm import GridLangVM
import sys
sys.path.append("..")
from gridcontrol.engine.ffi import GridControlFFI

def fake_ffi(vm, args):
	return 0

if __name__ == "__main__":
	if len(sys.argv) > 1:
		fn = sys.argv[1]
	else:
		fn = "code.gridlang"

	with open(fn) as fh:
		code = fh.read()
	c = GridLangParser.parse(code, constants=GridControlFFI.CONSTANTS)

	vm = None
	data = None

	while 1:
		if vm is not None:
			data = vm.freeze()
		vm = GridLangVM()
		vm.ffi = fake_ffi
		vm.set_code(c)
		if data is not None:
			vm.thaw(data)
		if vm.run(10):
			break
		
