#
# This is the server runtime. It creates a server that listens on port configured in config.
#

from twisted.internet import reactor
from autobahn.websocket import WebSocketServerFactory, listenWS

from server import VectorServerProtocol

import config

factory = WebSocketServerFactory(config.SERVER_ADDRESS)
factory.protocol = VectorServerProtocol
listenWS(factory)
reactor.run()
