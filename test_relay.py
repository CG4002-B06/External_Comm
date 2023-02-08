
from relay.relay_server import RelayServer
from queue import Queue

from test_pseudo_ai import PseudoAI

if __name__ == "__main__":
    receive_metrics = Queue()
    action_queue = Queue()
    ai = PseudoAI(receive_metrics, action_queue).start()
    server = RelayServer(receive_metrics).serve_request()


