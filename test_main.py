import json
import threading
from queue import Queue
from threading import Event, Thread

from constants.Actions import Action
from constants.constant import END_GAME
from mqtt.Consumer import Consumer
from mqtt.Producer import Producer
from game_engine.eval_client import Eval_Client
from game_engine.GameEngine import GameEngine
from constants import constant
import relay.relay_server as rs
# import AI.ai_prediction as ai

action_queues = [Queue(), Queue()]  # queue to receive action messages determined by AI
visualizer_queue = Queue()  # queue to send messages to the publisher
grenadeQuery_queue = Queue()  # consumer receive grenade query message and put it in the queue for visualizer
relay_queue = Queue()
event_queue = Queue()
has_logout = [Event(), Event()]
barrier = threading.Barrier(3)

if __name__ == '__main__':
    if constant.ONE_PLAYER:
        has_logout[1].set()

    producer1 = Producer(visualizer_queue, constant.PUBLISH_TOPIC_V, has_logout)
    producer1.start()
    print("producer 1 starts")

    producer2 = Producer(event_queue, constant.PUBLISH_TOPIC_E, has_logout)
    producer2.start()
    print("producer 2 starts")
    event_queue.put(json.dumps({"p1": constant.WAIT_SENSOR_INIT_MESSAGE,
                                "p2": constant.WAIT_SENSOR_INIT_MESSAGE}))

    consumer = Consumer(grenadeQuery_queue, has_logout)
    consumer.start()
    print("consumer starts")

    relay_server = rs.RelayServer(action_queues, relay_queue, event_queue, barrier, has_logout)
    relay_server.start()
    print("relay server starts")

    # ai1 = Thread(target=ai.start_prediction, args=(action_queues[0], event_queue, has_logout[0], 0))
    # ai2 = Thread(target=ai.start_prediction, args=(action_queues[1], event_queue, has_logout[1], 1))
    # ai1.start()
    # ai2.start()
    # print("ai starts")

    print("main thread waits at the barrier")
    barrier.wait()

    eval_client = None
    if constant.HAS_EVAL:
        eval_client = Eval_Client(constant.IP_ADDRESS, constant.PORT_NUMBER)
    game_engine = GameEngine(action_queues, visualizer_queue, grenadeQuery_queue, relay_queue,
                             has_logout, constant.ONE_PLAYER, eval_client)
    game_engine.start()
    print("game engine start")

    event_queue.put(json.dumps({
        "p1": constant.INIT_COMPLETE_MSG,
        "p2": constant.INIT_COMPLETE_MSG
    }))

    action1, action2 = input(), input()
    action_queues[0].put([Action(action1), {}])
    action_queues[1].put([Action(action2), {}])

    game_engine.join()
    event_queue.put(END_GAME)
    visualizer_queue.put(END_GAME)
    relay_queue.put(END_GAME)

    # ai1.join()
    # ai2.join()
    relay_server.join()
    consumer.join()
    producer1.join()
    producer2.join()

    print("bye")
