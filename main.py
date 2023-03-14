from queue import Queue
from threading import Event, Thread

from constants.Actions import Action
from mqtt.Consumer import Consumer
from mqtt.Producer import Producer
from game_engine.eval_client import Eval_Client
from constants import eval_server_constant, game_state
from game_engine import GameEngine
from constants import mqtt_constant, game_state
from relay.relay_server import RelayServer

# import AI.ai_prediction as ai

action_queues = [Queue(), Queue()]  # queue to receive action messages determined by AI
visualizer_queue = Queue()  # queue to send messages to the publisher
grenadeQuery_queue = Queue()  # consumer receive grenade query message and put it in the queue for visualizer
hp_queue = Queue()
has_logout = [Event(), Event()]


def user_input():
    while True:
        data = input()
        try:
            action_queues[0].put([Action(data), {"p1": True}])
        except Exception:
            return


if __name__ == '__main__':
    if game_state.ONE_PLAYER:
        has_logout[1].set()

    eval_client = None
    if game_state.HAS_EVAL:
        eval_client = Eval_Client(eval_server_constant.IP_ADDRESS, eval_server_constant.PORT_NUMBER)
    game_engine = GameEngine.GameEngine(action_queues, visualizer_queue, grenadeQuery_queue, hp_queue,
                                        has_logout, game_state.ONE_PLAYER, eval_client)
    game_engine.start()
    print("game engine start")

    producer = Producer(visualizer_queue, mqtt_constant.PUBLISH_TOPIC_V, has_logout)
    producer.start()
    print("producer start")

    consumer = Consumer(grenadeQuery_queue, has_logout)
    consumer.start()
    print("consumer start")

    relay_server = RelayServer(action_queues[0], hp_queue, has_logout)
    relay_server.start()
    print("relay server start")


    # ai = Thread(target=ai.start_prediction, args=(action_queues[0], has_logout))
    # ai.start()
    # print("ai start")
    # while True:
    #     data = input()
    #     action_queues[1].put([Action(data), {"p1": True}])

    # ai.join()
    relay_server.join()
    consumer.join()
    producer.join()
    game_engine.join()
    print("bye")
