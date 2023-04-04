import json
import random
from socket import *
from threading import Thread, Lock, Event, Semaphore
import struct
from constants.Actions import Action
from constants import constant
from constants.constant import END_GAME

VEST_FORMAT = '<c2s?'
GLOVES_FORMAT = '<c3s6h'

cached_data = [[], []]
lk = [Lock(), Lock()]
queue_full = [Event(), Event()]
semaphore = Semaphore(0)

class bcolors:
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class RelayServer(Thread):
    server_port = 6666

    def __init__(self, action_queue, relay_queue,
                 event_queue, barrier, has_logout):
        super().__init__()
        self.barrier = barrier
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(('', RelayServer.server_port))
        self.server_socket.listen(1)
        self.action_queue = action_queue
        self.relay_queue = relay_queue
        self.event_queue = event_queue
        self.has_logout = has_logout

    def recv_msg(self, connection_socket):
        data = b''
        while not data.endswith(b'_'):
            _d = connection_socket.recv(1)
            if not _d:
                data = b''
                continue
            data += _d
        data = data.decode("utf-8")
        length = int(data[:-1])

        data = b''
        while len(data) < length:
            _d = connection_socket.recv(length - len(data))
            if not _d:
                data = b''
                continue
            data += _d
        return data

    def serve_request(self, connection_socket):
        global cached_data

        hello_packet = self.recv_msg(connection_socket).decode()
        while hello_packet[0] != 'R':
            hello_packet = self.recv_msg(connection_socket).decode()
            print(hello_packet)
        print("hello packet: " + hello_packet)
        id = int(hello_packet[1])
        print(f"player{id}'s sensor has initialised")
        self.barrier.wait()

        while not self.has_logout[id - 1].is_set():
            data = self.recv_msg(connection_socket)
            if data == b'B':
                break
            if data == b'Q1' or data == b'Q2':
                self.handle_beetle_disconnection(id, connection_socket)
                continue

            if len(data) == 4:
                msg = struct.unpack(VEST_FORMAT, data)
                self.action_queue[id - 1].put([Action.SHOOT, {"p" + str(id): msg[2]}])
                print(msg)

            else:
                msg = struct.unpack(GLOVES_FORMAT, data)
                print(msg)
                lk[id - 1].acquire()
                cached_data[id - 1].append(list(msg)[2:])

                if len(cached_data[id - 1]) >= constant.ROW_SIZE:
                    queue_full[id - 1].set()

                lk[id - 1].release()

        connection_socket.close()
        lk[id - 1].acquire()
        cached_data[id - 1].clear()
        cached_data[id - 1].append(END_GAME)
        queue_full[id - 1].set()
        lk[id - 1].release()
        print("connection socket " + str(id) + " closes")

    def handle_beetle_disconnection(self, id, connection_socket):
        print(f"{id} disconnected")
        self.event_queue.put(json.dumps({
            "id": random.randint(0, 9999),
            "p1": None,
            "p2": None,
            f"p{id}": constant.SENSOR_DISCONNECT_MSG}))
        lk[id - 1].acquire()
        cached_data[id - 1].clear()
        lk[id - 1].release()

        while connection_socket.recv(2) != f'R{id}'.encode():
            pass
        self.event_queue.put(json.dumps({
            "id": random.randint(0, 9999),
            "p1": None,
            "p2": None,
            f"p{id}": constant.SENSOR_RECONNECT_MSG
        }))
        print(f"connection {id} is back")

    def run(self):
        threads = []

        connection_socket1, client_addr1 = self.server_socket.accept()
        print("receive sending channel 1")
        connection_socket2, client_addr2 = self.server_socket.accept()
        print("receive sending channel 2")
        send_thread = Thread(target=send, args=(connection_socket1, connection_socket2, self.relay_queue))
        send_thread.start()
        threads.append(send_thread)

        for i in range(0, 2):
            connection, client_addr = self.server_socket.accept()
            t = Thread(target=self.serve_request, args=(connection,))
            t.start()
            threads.append(t)
            semaphore.release()

        for thread in threads:
            thread.join()
        self.server_socket.close()
        print("relay server closes")


def send(send_socket1, send_socket2, relay_queue):
    print("sending channel is ready")
    send_socket1.sendall(b'E')
    semaphore.acquire()
    send_socket2.sendall(b'E')
    while True:
        data = relay_queue.get()
        if data == END_GAME:
            break
        print("send data: " + str(data))
        send_socket1.sendall(str(len(data)).encode("utf8") + b'_' + data.encode("utf8"))
        send_socket2.sendall(str(len(data)).encode("utf8") + b'_' + data.encode("utf8"))
    print("send socket closes")
