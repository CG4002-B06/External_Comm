from queue import Queue
from threading import Thread

from mqtt.Consumer import Consumer
from mqtt.Producer import Producer
from game_engine.eval_client import Eval_Client
from constants import eval_server_constant
from game_engine import GameEngine
from constants import mqtt_constant, game_state
from relay.relay_server import RelayServer
import AI.ai_prediction as ai

action_queues = [Queue(), Queue()]  # queue to receive action messages determined by AI
visualizer_queue = Queue()  # queue to send messages to the publisher
grenadeQuery_queue = Queue()  # consumer receive grenade query message and put it in the queue for visualizer
hp_queue = Queue()

if __name__ == '__main__':
    eval_client = None
    if game_state.HAS_EVAL:
        eval_client = Eval_Client(eval_server_constant.IP_ADDRESS, eval_server_constant.PORT_NUMBER)
    game_engine = GameEngine.GameEngine(action_queues, visualizer_queue, grenadeQuery_queue,
                             hp_queue, game_state.ONE_PLAYER, eval_client)
    game_engine.start()
    print("game engine start")

    producer = Producer(visualizer_queue, mqtt_constant.PUBLISH_TOPIC_V)
    producer.start()
    print("producer start")

    consumer = Consumer(grenadeQuery_queue)
    consumer.start()
    print("consumer start")

    relay_server = RelayServer(action_queues[0], hp_queue)
    relay_server.start()
    print("relay server start")

    ai = Thread(target=ai.start_prediction, args=(action_queues[0],))
    ai.start()
    print("ai start")

    ai.join()
    relay_server.join()
    consumer.join()
    producer.join()
    game_engine.join()
    print("bye")
