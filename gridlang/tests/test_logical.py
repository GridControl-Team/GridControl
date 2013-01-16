import unittest

from tests.utils import inline_src, get_result

class TestLogical(unittest.TestCase):
	def test_simple(self):
		src = inline_src("AND << 1 1")
		self.assertEqual(get_result(src), 1)

		src = inline_src("AND << 1 0")
		self.assertEqual(get_result(src), 0)

		src = inline_src("AND << 0 1")
		self.assertEqual(get_result(src), 0)

		src = inline_src("AND << 0 0")
		self.assertEqual(get_result(src), 0)
	
		src = inline_src("OR << 1 1")
		self.assertEqual(get_result(src), 1)

		src = inline_src("OR << 1 0")
		self.assertEqual(get_result(src), 1)

		src = inline_src("OR << 0 1")
		self.assertEqual(get_result(src), 1)

		src = inline_src("OR << 0 0")
		self.assertEqual(get_result(src), 0)
	
