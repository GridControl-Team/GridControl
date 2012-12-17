from urls import urls
import tornado.web

class GridStreamApp(tornado.web.Application):
	def __init__(self, *args, **kwargs):
		super(GridStreamApp, self).__init__(*args, **kwargs)
