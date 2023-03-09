import struct
import time
from queue import Queue
from threading import Event, Thread
from relay.relay_client import *
import random

VEST_FORMAT = '<c2s?'
GLOVES_FORMAT = '<c3s6h'
event = Event()
data_queue, response_queue = Queue(), Queue()


if __name__ == "__main__":
    t = Thread(target=run, args=(data_queue, response_queue, event)).start()
    while True:

        data = struct.pack(
            GLOVES_FORMAT,
            bytes("D",'utf8'),
            bytes("GL1", 'utf8'),
            random.randint(0, 10000),
            random.randint(0, 10000),
            random.randint(0, 10000),
            random.randint(0, 10000),
            random.randint(0, 10000),
            random.randint(0, 10000)
        )
        data_queue.put(data)
        time.sleep(0.1)



