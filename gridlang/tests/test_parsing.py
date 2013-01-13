import unittest

from tests.utils import get_src, parse, exe, extract

class TestSimpleParsing(unittest.TestCase):
	
	def test_basic(self):
		src = get_src("blank")
		parse(src)

		src = get_src("win")
		parse(src)
		
		src = get_src("factorial")
		parse(src)

		src = get_src("factorial_short")
		parse(src)

class TestSimpleExecution(unittest.TestCase):
	def test_factorial(self):
		src = get_src("factorial")
		c = parse(src)
		vm = exe(c)
		self.assertEqual(extract(vm), 479001600)

		src = get_src("factorial_short")
		c = parse(src)
		vm = exe(c)
		self.assertEqual(extract(vm), 479001600)
	
	def test_blanks(self):
		src = get_src("blank")
		c = parse(src)
		vm = exe(c)
		self.assertEqual(len(vm.data), 0)
		self.assertEqual(len(vm.exe), 0)
		self.assertEqual(len(vm.reg), 0)
		
		src = get_src("win")
		c = parse(src)
		vm = exe(c)
		self.assertEqual(len(vm.data), 0)
		self.assertEqual(len(vm.exe), 0)
		self.assertEqual(len(vm.reg), 0)

