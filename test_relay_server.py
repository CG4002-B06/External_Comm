from queue import Queue
from threading import Thread

from relay.relay_server import RelayServer
import AI.ai_prediction as ai
action_queue, hp_queue = Queue()

if __name__ == '__main__':
    RelayServer(action_queue, hp_queue).start()
    t = Thread(target=ai.start_prediction, args=(action_queue,))
    t.start()
    t.join()



