import struct
import time
from queue import Queue
from threading import Event, Thread
from relay.relay_client import *

VEST_FORMAT = '<c2s?'
event = Event()
data_queue, response_queue = Queue(), Queue()

if __name__ == "__main__":
    t = Thread(target=run, args=(data_queue, response_queue, event)).start()
    while True:
        data = struct.pack(VEST_FORMAT, bytes("D",'utf8'), bytes("V1", 'utf8'), False)
        data_queue.put(data)
        time.sleep(0.4)



