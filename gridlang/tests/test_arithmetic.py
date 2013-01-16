import unittest
from decimal import Decimal

from tests.utils import inline_src, get_result

class TestArithmetic(unittest.TestCase):
	def test_ints(self):
		src = inline_src("ADD << 1 2")
		self.assertEqual(get_result(src), 3)
	
		src = inline_src("MINUS << 3 2")
		self.assertEqual(get_result(src), 1)
	
		src = inline_src("MUL << 2 3")
		self.assertEqual(get_result(src), 6)

		src = inline_src("DIV << 6 3")
		self.assertEqual(get_result(src), 2)

		src = inline_src("DIV << 5 3")
		self.assertEqual(get_result(src), 1)

		src = inline_src("MOD << 5 3")
		self.assertEqual(get_result(src), 2)

		src = inline_src("ABS << -2")
		self.assertEqual(get_result(src), 2)

		src = inline_src("ABS << 2")
		self.assertEqual(get_result(src), 2)

	def test_decimals(self):
		src = inline_src("ADD << 1.1 2.2")
		self.assertEqual(get_result(src), Decimal('3.3'))
	
		src = inline_src("MINUS << 3.3 2.2")
		self.assertEqual(get_result(src), Decimal('1.1'))
	
		src = inline_src("MUL << 0.5 2.0")
		self.assertEqual(get_result(src), Decimal('1.0'))

		src = inline_src("DIV << 2.0 0.5")
		self.assertEqual(get_result(src), 4)
		self.assertIsInstance(get_result(src), int)

		src = inline_src("MOD << 5.0 3.0")
		self.assertEqual(get_result(src), Decimal('2.0'))
		self.assertIsInstance(get_result(src), Decimal)

		src = inline_src("ABS << -2.1")
		self.assertEqual(get_result(src), Decimal('2.1'))

		src = inline_src("ABS << 2.1")
		self.assertEqual(get_result(src), Decimal('2.1'))

