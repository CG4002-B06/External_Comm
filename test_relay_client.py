import struct
import time
from queue import Queue
from threading import Event
from relay.relay_client import *
import random

VEST_FORMAT = '<c2s?'
GLOVES_FORMAT = '<c3s6h'
event = Event()
data_queue1, data_queue2 = Queue(), Queue()


if __name__ == "__main__":
    t1 = Thread(target=run, args=(data_queue1, event, 1)).start()
    time.sleep(10)
    t2 = Thread(target=run, args=(data_queue2, event, 2)).start()
    while True:
        command = input()
        if command == "D1":
            data_queue1.put(b'D')
        elif command == "D2":
            data_queue2.put(b'D')
        elif command == "R1":
            data_queue1.put(b'R')
        elif command == "R2":
            data_queue2.put(b'R')
        else:
            event.set()
            break
        #
        # data = struct.pack(
        #     GLOVES_FORMAT,
        #     bytes("D",'utf8'),
        #     bytes("GL1", 'utf8'),
        #     random.randint(0, 10000),
        #     random.randint(0, 10000),
        #     random.randint(0, 10000),
        #     random.randint(0, 10000),
        #     random.randint(0, 10000),
        #     random.randint(0, 10000)
        # )
        # data_queue.put(data)
        # time.sleep(0.1)



