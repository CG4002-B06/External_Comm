from queue import Queue

from mqtt.Consumer import Consumer
from mqtt.Producer import Producer
from constants.Actions import Action
from game_engine.eval_client import Eval_Client
from constants import eval_server_constant, mqtt_constant
from game_engine.GameEngine import GameEngine
from relay.relay_server import RelayServer

action_queues = [Queue(), Queue()]  # queue to receive action messages determined by AI
visualizer_queue = Queue()  # queue to send messages to the publisher
grenadeQuery_queue = Queue() # consumer receive grenade query message and put it in the queue for visualizer
hp_queue = Queue()

if __name__ == '__main__':
    # eval_client = Eval_Client(eval_server_constant.IP_ADDRESS, eval_server_constant.PORT_NUMBER)
    eval_client = None
    RelayServer(action_queues[0], hp_queue)
    GameEngine(action_queues, visualizer_queue, grenadeQuery_queue, hp_queue, eval_client).start()
    Producer(visualizer_queue, mqtt_constant.PUBLISH_TOPIC_V).start()
    # Producer(hp_queue, mqtt_constant.PUBLISH_TOPIC_R).start()

    # consumer = Consumer(grenadeQuery_queue).start()

    while True:
        action1 = [Action(input()), {"p1": True}]
        action2 = [Action('none'), {"p2": True}]
        action_queues[0].put(action1)
        action_queues[1].put(action2)


