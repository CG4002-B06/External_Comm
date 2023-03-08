from queue import Queue

from relay.relay_server import RelayServer


receive_metric_queue = Queue()  # queue to receive metrics from relay node
action_queue = Queue()
hp_queue = Queue()
if __name__ == '__main__':
    server = RelayServer(receive_metric_queue, action_queue, hp_queue).run()

