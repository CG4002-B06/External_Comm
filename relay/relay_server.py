from socket import *
from threading import Thread
import struct
from ClassificationAlgo import predict

from constants.Actions import Action

VEST_FORMAT = '<c2s?'
GLOVES_FORMAT = '<c3s6h'

class RelayServer:
    server_port = 6666

    def __init__(self, metrics_queue, action_queue, hp_queue):
        super().__init__()
        self.metrics_queue = metrics_queue
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('', RelayServer.server_port))
        self.server_socket.listen(1)
        self.hp_queue = hp_queue
        self.action_queue = action_queue
        self.hp = ['100', '100']

    def serve_request(self, connection_socket):
        cache_data = []
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
                while not self.hp_queue.empty():
                    self.hp = self.hp_queue.get()
                msg = struct.unpack(VEST_FORMAT, data)
                player_id = msg[1][-1] - ord('0')
                connection_socket.sendall(self.hp[player_id].encode("utf8"))
                self.action_queue.put([Action.SHOOT, msg[2]])
                print(msg)
            else:
                msg = struct.unpack(GLOVES_FORMAT, data)
                self.metrics_queue.put(msg)
                cache_data.append(list([msg[2:]]))
                if len(cache_data) >= 50:
                    self.action_queue.put(predict(cache_data))
                    cache_data.clear()
                print(msg)

    def run(self):
        while True:
            connection_socket, client_addr = self.server_socket.accept()
            print("accept new connection")
            Thread(target=self.serve_request, args=(connection_socket,)).start()
