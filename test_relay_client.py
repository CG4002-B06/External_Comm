from queue import Queue
from threading import Event
from relay.relay_client import *

VEST_FORMAT = '<c2s?'
GLOVES_FORMAT = '<c3s6h'
event1, event2 = Event(), Event()
data_queue1, data_queue2 = Queue(), Queue()

def recv_msg(socket):
    data = b''
    while not data.endswith(b'_'):
        data += socket.recv(1)

    data = data.decode("utf-8")
    length = int(data[:-1])
    data = b''
    while len(data) < length:
        data += socket.recv(length - len(data))
    return data


if __name__ == "__main__":
    client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client1.connect(("localhost", 6674))
    t1 = Thread(target=run, args=(data_queue1, event1, 1)).start()
    time.sleep(5)
    t2 = Thread(target=run, args=(data_queue2, event2, 2)).start()

    recv_msg(client1)
    event1.set()
    event2.set()
    client1.close()







