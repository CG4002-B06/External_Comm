from queue import Queue

from mqtt.Consumer import Consumer

if __name__ == "__main__":
    q = Queue()
    Consumer(q).run()