import unittest

from tests.utils import inline_src, get_result

class TestBitwise(unittest.TestCase):
	def test_simple(self):
		src = inline_src("BAND << 1 1")
		self.assertEqual(get_result(src), 1)

		src = inline_src("BAND << 1 0")
		self.assertEqual(get_result(src), 0)

		src = inline_src("BAND << 0 1")
		self.assertEqual(get_result(src), 0)

		src = inline_src("BAND << 0 0")
		self.assertEqual(get_result(src), 0)
	
		src = inline_src("BOR << 1 1")
		self.assertEqual(get_result(src), 1)

		src = inline_src("BOR << 1 0")
		self.assertEqual(get_result(src), 1)

		src = inline_src("BOR << 0 1")
		self.assertEqual(get_result(src), 1)

		src = inline_src("BOR << 0 0")
		self.assertEqual(get_result(src), 0)

		src = inline_src("BXOR << 0 0")
		self.assertEqual(get_result(src), 0)

		src = inline_src("BXOR << 0 1")
		self.assertEqual(get_result(src), 1)

		src = inline_src("BXOR << 1 0")
		self.assertEqual(get_result(src), 1)

		src = inline_src("BXOR << 1 1")
		self.assertEqual(get_result(src), 0)

