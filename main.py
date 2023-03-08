from queue import Queue
from threading import Thread

from mqtt.Consumer import Consumer
from mqtt.Producer import Producer
from game_engine.eval_client import Eval_Client
from constants import eval_server_constant
from game_engine.GameEngine import GameEngine
from constants import mqtt_constant
from relay.relay_server import RelayServer
import AI.ai_prediction as ai

action_queues = [Queue(), Queue()]  # queue to receive action messages determined by AI
visualizer_queue = Queue()  # queue to send messages to the publisher
grenadeQuery_queue = Queue() # consumer receive grenade query message and put it in the queue for visualizer
hp_queue = Queue()

if __name__ == '__main__':
    eval_client = Eval_Client(eval_server_constant.IP_ADDRESS, eval_server_constant.PORT_NUMBER)
    # eval_client = None
    GameEngine(action_queues, visualizer_queue, grenadeQuery_queue, hp_queue, eval_client).start()
    Producer(visualizer_queue, mqtt_constant.PUBLISH_TOPIC_V).start()
    Producer(hp_queue, mqtt_constant.PUBLISH_TOPIC_R).start()
    consumer = Consumer(grenadeQuery_queue).start()
    RelayServer(action_queues).run()
    Thread(target=ai.start_prediction, args=(action_queues[0],)).start()
    Thread(target=ai.start_prediction, args=(action_queues[1],)).start()



