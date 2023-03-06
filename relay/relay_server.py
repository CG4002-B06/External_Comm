from socket import *
import concurrent.futures
from threading import Thread


class RelayServer:
    server_port = 6666

    def __init__(self, metrics_queue, hp_queue):
        super().__init__()
        self.metrics_queue = metrics_queue
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('', RelayServer.server_port))
        self.server_socket.listen(1)
        self.hp_queue = hp_queue
        self.hp = ['100', '100']

    def serve_request(self, connection_socket, player_id):
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
            msg = data.decode("utf8")
            if not self.hp_queue.empty():
                self.hp = self.hp_queue.get()
            connection_socket.sendall(self.hp[player_id].encode("utf8"))
            self.metrics_queue.put(msg)

    def run(self):
        connection_socket, client_addr = self.server_socket.accept()
        Thread(target=self.serve_request, args=(connection_socket, 0)).start()
        input()