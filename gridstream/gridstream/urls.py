import views
from tornadio2 import TornadioRouter, SocketConnection
import tornadoredis

class tornadioConnection(SocketConnection):
	__endpoints__ = {
		'/tornado/stream': views.StreamComm,
	}

socketIORouter = TornadioRouter(
	tornadioConnection, {
		'enabled_protocols': [
			'websocket',
			'xhr-polling',
			'jsonp-polling'
		]
	}
)

urls = socketIORouter.apply_routes([])
