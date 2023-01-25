from socket import *
import concurrent.futures


class relay_server:
    server_port = 6666
    MAX_CONNECTIONS = 3

    def __init__(self, metrics_queue):
        super().__init__()
        self.metrics_queue = metrics_queue
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('', relay_node_receiver.server_port))
        self.server_socket.listen()
        self.executor = concurrent.futures.ThreadPoolExecutor(relay_node_receiver.MAX_CONNECTIONS)
        
    def request_process(self, client, addr):
        message = client.recv(2048)
        client.send(message)
        self.metrics_queue.put(message)

    def serve_request(self):
        while True:
            connection_socket, client_addr = self.server_socket.accept()
            print("accept requests from" + str(client_addr))
            self.executor.submit(request_process, connection_socket, client_addr)
