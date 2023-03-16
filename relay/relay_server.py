from socket import *
import pandas as pd
from threading import Thread, Lock, Event
import struct
from AI.StartIdentification import detect_move
from constants.Actions import Action
from constants import ai_constant

VEST_FORMAT = '<c2s?'
GLOVES_FORMAT = '<c3s6h'

cached_data = []
lk = Lock()
event, connection_established = Event(), Event()
eval_client = Event()
disconnection = Event()

class RelayServer(Thread):
    server_port = 6674

    def __init__(self, action_queue, hp_queue, has_logout):
        super().__init__()
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('', RelayServer.server_port))
        self.server_socket.listen(1)
        self.action_queue = action_queue
        self.hp_queue = hp_queue
        self.has_logout = has_logout

    def serve_request(self, connection_socket):
        global cached_data
        hello_packet = connection_socket.recv(2).decode()
        connection_socket.send(b'A')
        print("hello packet: " + hello_packet)
        player_id = int(hello_packet[1])

        send_socket, addr = self.server_socket.accept()
        send_thread = Thread(target=send, args=(send_socket, self.hp_queue, self.has_logout[player_id - 1]))
        send_thread.start()
        print("second connection established")
        connection_established.set()
        eval_client.set()


        flag = False
        while not self.has_logout[player_id - 1].is_set():
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
            if data == b'B':
                break
            if data == b'D':
                print("disconnected")
                disconnection.set()
                while connection_socket.recv(1) != b'R':
                    pass
                disconnection.clear()
                print("connection is back")
                continue

            if len(data) == 4:
                msg = struct.unpack(VEST_FORMAT, data)
                self.action_queue.put([Action.SHOOT, {"p" + str(player_id): msg[2]}])
                print(msg)
            else:
                msg = struct.unpack(GLOVES_FORMAT, data)
                lk.acquire()
                cached_data.append(list(msg)[2:])
                print(len(cached_data))
                if not flag and len(cached_data) >= ai_constant.DETECT_MOVE_SIZE:
                    flag = detect_move(pd.DataFrame(cached_data[0: ai_constant.DETECT_MOVE_SIZE]))
                    cached_data = cached_data[2:]

                if flag and len(cached_data) >= ai_constant.ROW_SIZE:
                    event.set()
                    flag = False
                lk.release()
                print(msg)

        connection_socket.close()
        send_thread.join()
        print("connection socket " + str(player_id) + "closes")


    def run(self):
        threads = []
        while not (self.has_logout[0].is_set() and self.has_logout[1].is_set()):
            connection_socket, client_addr = self.server_socket.accept()
            t = Thread(target=self.serve_request, args=(connection_socket,))
            t.start()
            threads.append(t)
            print("accept the first connection")
            connection_established.wait()
            connection_established.clear()

        for thread in threads:
            thread.join()
        print("relay server closes")


def send(send_socket, hp_queue, has_logout):
    while not has_logout.is_set():
        data = hp_queue.get()
        print("send data: " + str(data))
        send_socket.sendall(str(len(data)).encode("utf8") + b'_' + data.encode("utf8"))
    send_socket.close()
    print("send socket closes")
