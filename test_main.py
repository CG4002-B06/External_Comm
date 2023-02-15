from queue import Queue

from mqtt.Consumer import Consumer
from mqtt.Producer import Producer
from game_engine.eval_client import Eval_Client
from constants import eval_server_constant
from game_engine.GameEngine import GameEngine
from relay.relay_server import RelayServer
from test_pseudo_ai import PseudoAI

receive_metric_queue = Queue()  # queue to receive metrics from relay node
action_queues = [Queue(), Queue()]  # queue to receive action messages determined by AI
visualizer_queue = Queue()  # queue to send messages to the publisher
grenadeQuery_queue = Queue() # consumer receive grenade query message and put it in the queue for visualizer

if __name__ == '__main__':
    eval_client = Eval_Client(eval_server_constant.IP_ADDRESS, eval_server_constant.PORT_NUMBER)
    pseudoAI = PseudoAI(receive_metric_queue, action_queues).start()
    game_engine = GameEngine(eval_client, action_queues, visualizer_queue, grenadeQuery_queue).start()
    producer = Producer(visualizer_queue).start()
    consumer = Consumer(grenadeQuery_queue).start()
    server = RelayServer(receive_metric_queue).run()

    while True:
        action = input("action: ") # Key in random action
        action_queues[0].put(action)
        action_queues[1].put('none')


