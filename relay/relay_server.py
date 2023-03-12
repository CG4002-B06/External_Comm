from socket import *
from threading import Thread, Lock, Event
import struct

from constants.Actions import Action
from constants import ai_constant


VEST_FORMAT = '<c2s?'
GLOVES_FORMAT = '<c3s6h'

cached_data = []
lk = Lock()
event, connection_established = Event(), Event()

class RelayServer(Thread):
    server_port = 6667

    def __init__(self, action_queue, hp_queue):
        super().__init__()
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('', RelayServer.server_port))
        self.server_socket.listen(1)
        self.action_queue = action_queue
        self.hp_queue = hp_queue

    def serve_request(self, connection_socket):
        hello_packet = connection_socket.recv(2).decode()
        connection_socket.send(b'A')
        print("hello packet: " + hello_packet)
        player_id = int(hello_packet[1])

        send_socket, addr = self.server_socket.accept()
        Thread(target=send, args=(send_socket, self.hp_queue)).start()
        print("second connection established")
        connection_established.set()

        while True:
            data = b''
            while not data.endswith(b'_'):
                _d = connection_socket.recv(1)
                if not _d:
                    data = b''
                    continue
                data += _d
            if len(data) == 0:
                print('no more data from the client')
                break
            data = data.decode("utf-8")
            length = int(data[:-1])
            # decode to get message
            data = b''
            while len(data) < length:
                _d = connection_socket.recv(length - len(data))
                if not _d:
                    data = b''
                    continue
                data += _d
            if len(data) == 0:
                print('no more data from the client')
                break

            if len(data) == 4:
                msg = struct.unpack(VEST_FORMAT, data)
                self.action_queue.put([Action.SHOOT, {"p" + str(player_id): msg[2]}])
                print(msg)
            else:
                msg = struct.unpack(GLOVES_FORMAT, data)
                lk.acquire()
                cached_data.append(list(msg)[2:])
                print(len(cached_data))
                if len(cached_data) >= ai_constant.ROW_SIZE:
                    event.set()
                lk.release()
                print(msg)

    def run(self):
        while True:
            connection_socket, client_addr = self.server_socket.accept()
            Thread(target=self.serve_request, args=(connection_socket,)).start()
            print("accept the first connection")
            connection_established.wait()
            connection_established.clear()

def send(socket, hp_queue):
    while True:
        print("waiting for data")
        data = hp_queue.get()
        print("send data: " + str(data))
        socket.sendall(str(len(data)).encode("utf8") + b'_' + data.encode("utf8"))
