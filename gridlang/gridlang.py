#!/usr/bin/env python
from parser import GridLangParser
from vm import GridLangVM
from errors import GridLangParseException
import sys
import signal

if __name__ == "__main__":
	if len(sys.argv) > 2:
		cmd = sys.argv[1]
		fn = sys.argv[2]
	elif len(sys.argv) > 1:
		cmd = 'run'
		fn = sys.argv[1]
	else:
		sys.exit("What file should I operate on?")

	with open(fn) as fh:
		code = fh.read()
		try:
			c = GridLangParser.parse(code)
		except GridLangParseException as e:
			sys.exit(e)
	
	if cmd == 'parse':
		c.print_code()
	else:
		vm = GridLangVM()
		vm.set_code(c)
		def sigint_handler(signal, frame):
			print ""
			print "SIGINT caught"
			vm.output_traceback()
			sys.exit(0)
		signal.signal(signal.SIGINT, sigint_handler)
		vm.run()
