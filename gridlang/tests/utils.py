import os

from vm import GridLangVM
from parser import GridLangParser

ROOT = os.path.abspath(os.path.dirname(__file__))

def get_src(sn):
	fn = os.path.join(ROOT, "src", "{0}.gridlang".format(sn))
	with open(fn) as fh:
		return fh.read()

def parse(cs):
	c = GridLangParser.parse(cs)
	return c

def exe(c):
	vm = GridLangVM()
	vm.capture_exception = True
	vm.set_code(c)
	vm.run()
	return vm

def exe_w_limits(c):
	vm = GridLangVM()
	vm.capture_exception = True
	vm.data_limit = 99
	vm.set_code(c)
	vm.run()
	return vm

def extract(vm):
	return vm.pop()
