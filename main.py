import threading
from queue import Queue
from threading import Event, Thread

from mqtt.Consumer import Consumer
from mqtt.Producer import Producer
from game_engine.eval_client import Eval_Client
from game_engine.GameEngine import GameEngine
from constants import mqtt_constant, game_state, eval_server_constant
from relay.relay_server import RelayServer

import AI.ai_prediction as ai

action_queues = [Queue(), Queue()]  # queue to receive action messages determined by AI
visualizer_queue = Queue()  # queue to send messages to the publisher
grenadeQuery_queue = Queue()  # consumer receive grenade query message and put it in the queue for visualizer
relay_queue = Queue()
has_logout = [Event(), Event()]
barrier = threading.Barrier(3)


if __name__ == '__main__':
    if game_state.ONE_PLAYER:
        has_logout[1].set()

    producer = Producer(visualizer_queue, mqtt_constant.PUBLISH_TOPIC_V, has_logout)
    producer.start()
    print("producer starts")

    consumer = Consumer(grenadeQuery_queue, has_logout)
    consumer.start()
    print("consumer starts")

    relay_server = RelayServer(action_queues[0], relay_queue, has_logout)
    relay_server.start()
    print("relay server starts")

    ai = Thread(target=ai.start_prediction, args=(action_queues[0], has_logout))
    ai.start()
    print("ai starts")

    print("main thread waits at the barrier")
    barrier.wait()
    
    eval_client = None
    if game_state.HAS_EVAL:
        eval_client = Eval_Client(eval_server_constant.IP_ADDRESS, eval_server_constant.PORT_NUMBER)
    game_engine = GameEngine(action_queues, visualizer_queue, grenadeQuery_queue, relay_queue,
                                        has_logout, game_state.ONE_PLAYER, eval_client)
    game_engine.start()
    print("game engine start")

    ai.join()
    relay_server.join()
    consumer.join()
    producer.join()
    game_engine.join()
    print("bye")
