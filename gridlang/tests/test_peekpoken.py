import unittest

from tests.utils import inline_src, parse, exe, exe_w_limits, extract
from errors import *

class TestPEEKPOKEN(unittest.TestCase):
	def test_basic(self):
		src = inline_src("<< 1 2 3; PEEKN << 0 3")
		c = parse(src)
		vm = exe(c)
		self.assertEqual(vm.data, [1, 2, 3, 1, 2, 3])

		src = inline_src("<< 1 2 3; PEEKN << 0 3; POKEN << 1 3")
		c = parse(src)
		vm = exe(c)
		self.assertEqual(vm.data, [1, 1, 2, 3])
