from queue import Queue
from mqtt.Producer import Producer
from game_engine.eval_client import Eval_Client
from constants import eval_server_constant
from game_engine.GameEngine import GameEngine
from constants import mqtt_constant

receive_metric_queue = Queue()  # queue to receive metrics from relay node
action_queue = Queue()  # queue to receive action messages determined by AI
visualizer_queue = Queue()  # queue to send messages to the publisher


if __name__ == '__main__':
    eval_client = Eval_Client(eval_server_constant.IP_ADDRESS, eval_server_constant.PORT_NUMBER)
    producer = Producer(visualizer_queue, mqtt_constant.PUBLISH_TOPIC_V).start()
    game_engine = GameEngine(eval_client, action_queue, visualizer_queue).start()

