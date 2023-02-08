from queue import Queue
from producer.Producer import Producer
from game_engine.eval_client import Eval_Client
from constants import eval_server_constant
from game_engine.GameEngine import GameEngine
from relay.relay_server import RelayServer
from .test_pseudo_ai import PseudoAI

receive_metric_queue = Queue()  # queue to receive metrics from relay node
action_queue = Queue()  # queue to receive action messages determined by AI
visualizer_queue = Queue()  # queue to send messages to the publisher

if __name__ == '__main__':
    eval_client = Eval_Client(eval_server_constant.IP_ADDRESS, eval_server_constant.PORT_NUMBER)
    pseudoAI = PseudoAI(receive_metric_queue, action_queue)
    game_engine = GameEngine(eval_client, action_queue, visualizer_queue).start()
    producer = Producer(visualizer_queue).start()
    server = RelayServer(receive_metric_queue).serve_request()

