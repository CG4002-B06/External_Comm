from queue import Queue

from relay.relay_server import RelayServer


receive_metric_queue = Queue()  # queue to receive metrics from relay node

if __name__ == '__main__':
    server = RelayServer(receive_metric_queue).serve_request()

