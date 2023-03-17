from socket import *
import pandas as pd
from threading import Thread, Lock, Event, Semaphore
import struct
from AI.StartIdentification import detect_move
from constants.Actions import Action
from constants import ai_constant
from main import barrier

VEST_FORMAT = '<c2s?'
GLOVES_FORMAT = '<c3s6h'

cached_data = [[], []]
lk = [Lock(), Lock()]
queue_full = [Event(), Event()]
connection_established = Semaphore(0)

class RelayServer(Thread):
    server_port = 6674

    def __init__(self, action_queue, relay_queue, has_logout):
        super().__init__()
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('', RelayServer.server_port))
        self.server_socket.listen(1)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.action_queue = action_queue
        self.hp_queue = relay_queue
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
        hello_packet = connection_socket.recv(2).decode()
        connection_socket.send(b'A')
        print("hello packet: " + hello_packet)
        id = int(hello_packet[1])

        send_socket, addr = self.server_socket.accept()
        send_thread = Thread(target=send, args=(send_socket, self.hp_queue, self.has_logout[id - 1]))
        send_thread.start()
        print(f"player:{id}'s sensor has initialised")
        connection_established.release()
        barrier.wait()

        flag = False
        while not self.has_logout[id - 1].is_set():
            data = self.recv_msg(connection_socket)
            if data == b'B':
                break
            if data == b'D':
                print("disconnected")
                while connection_socket.recv(1) != b'R':
                    pass
                print("connection is back")
                continue

            if len(data) == 4:
                msg = struct.unpack(VEST_FORMAT, data)
                self.action_queue.put([Action.SHOOT, {"p" + str(id): msg[2]}])

            else:
                msg = struct.unpack(GLOVES_FORMAT, data)
                lk[id - 1].acquire()
                cached_data[id - 1].append(list(msg)[2:])

                if not flag and len(cached_data[id - 1]) >= ai_constant.DETECT_MOVE_SIZE:
                    flag = detect_move(pd.DataFrame(cached_data[id - 1][0: ai_constant.DETECT_MOVE_SIZE]))
                    cached_data[id - 1] = cached_data[id - 1][2:]

                if flag and len(cached_data[id - 1]) >= ai_constant.ROW_SIZE:
                    flag = False
                    queue_full[id - 1].set()

                lk[id - 1].release()

        connection_socket.close()
        send_thread.join()
        print("connection socket " + str(id) + "closes")


    def run(self):
        threads = []
        for i in range(0, 10):
            connection_socket, client_addr = self.server_socket.accept()
            t = Thread(target=self.serve_request, args=(connection_socket,))
            t.start()
            threads.append(t)
            connection_established.acquire()

        for thread in threads:
            thread.join()
        self.server_socket.close()
        print("relay server closes")


def send(send_socket, relay_queue, has_logout):
    while not has_logout.is_set():
        data = relay_queue.get()
        print("send data: " + str(data))
        send_socket.sendall(str(len(data)).encode("utf8") + b'_' + data.encode("utf8"))
    send_socket.close()
    print("send socket closes")
