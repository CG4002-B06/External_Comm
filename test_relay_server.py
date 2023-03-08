from queue import Queue
from threading import Thread

from relay.relay_server import RelayServer
import AI.ai_prediction as ai
action_queue = Queue()

if __name__ == '__main__':
    RelayServer(action_queue).run()
    Thread(target=ai.start_ai, args=(action_queue,)).start()



