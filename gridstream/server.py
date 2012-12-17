import os.path
from tornado.options import define, options
from tornadio2 import SocketServer
import gridstream

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

define("root", default=BASE_PATH)
define("port", default=8001, help="Server port")

settings = {
	"debug": True,
	"socket_io_port": 8002,
}

application = gridstream.GridStreamApp(
	gridstream.urls,
	**settings
)

if __name__ == "__main__":
	application.listen(options.port)
	print "Starting on {0}".format(options.port)
	SocketServer(application)
