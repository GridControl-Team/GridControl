import unittest

from tests.utils import get_src, parse, exe, exe_w_limits, extract
from errors import *

class TestDUPN(unittest.TestCase):
	def test_basic(self):
		src = get_src("dupn")
		c = parse(src)
		vm = exe(c)
		self.assertEqual(len(vm.data), 100)

		with self.assertRaises(GridLangExecutionException):
			vm = exe_w_limits(c)
