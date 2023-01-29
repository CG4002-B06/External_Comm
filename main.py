from queue import Queue
from Producer import Producer
from Eval import Eval
from constants import eval_server
from GameEngine import GameEngine

receive_metric_queue = Queue()  # queue to receive metrics from relay node
action_queue = Queue()  # queue to receive action messages determined by AI
visualizer_queue = Queue()  # queue to send messages to the publisher


if __name__ == '__main__':
    eval_client = Eval(eval_server.IP_ADDRESS, eval_server.PORT_NUMBER)
    producer = Producer(visualizer_queue).start()
    game_engine = GameEngine(eval_client, action_queue, visualizer_queue).start()

