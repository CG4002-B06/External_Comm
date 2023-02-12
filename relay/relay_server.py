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
            receive_data_length = b''
            while not receive_data_length.endswith(b'_'):
                receive_data_length += connection_socket.recv(1)

            receive_data_length = receive_data_length.decode("utf8")
            length = int(receive_data_length[:-1])
            data = b''
            while len(data) < length:
                data += connection_socket.recv(length - len(data))

            message = data.decode("utf8")
            print("receive message\t" + str(message))
            self.metrics_queue.put(message)

    def run(self):
        while True:
            connection_socket, client_addr = self.server_socket.accept()
            print("accept connection")
            Thread(target=self.serve_request, args=(connection_socket,)).start()
