from socket import *
import concurrent.futures
from threading import Thread


class RelayServer:
    server_port = 6666
    MAX_CONNECTIONS = 3

    def __init__(self, metrics_queue):
        super().__init__()
        self.metrics_queue = metrics_queue
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('', RelayServer.server_port))
        self.server_socket.listen(1)

    def serve_request(self, connection_socket):
        while True:
            try:
                # decode to get length
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
                print("receive message: " + msg)
                self.metrics_queue.put(msg)
            except Exception:
                print('Exception on Connection')
                break

    def run(self):
        while True:
            connection_socket, client_addr = self.server_socket.accept()
            print("accept connection")
            Thread(target=self.serve_request, args=(connection_socket,)).start()
