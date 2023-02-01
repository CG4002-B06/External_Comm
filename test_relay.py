from relay.relay_server import RelayServer
from queue import Queue

receive_metrics = Queue()
server = RelayServer(receive_metrics).serve_request()

