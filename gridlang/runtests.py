import unittest

if __name__ == "__main__":
	import os
	import sys
	sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
	tl = unittest.TestLoader()
	suite = tl.discover("tests")
	runner = unittest.TextTestRunner(verbosity=1 + sys.argv.count('-v'))
	raise SystemExit(not runner.run(suite).wasSuccessful())
