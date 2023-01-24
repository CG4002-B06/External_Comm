from socket import *
import concurrent.futures

server_port = 6666
MAX_CONNECTIONS = 2

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('', server_port))
server_socket.listen()
print('Server is ready to connect')

def serve_connection(client, addr):
    while True:
        message = client.recv(2048)
        client.send(message)
        print("receive message: " + message)
        if message.decode() == 'close':
            break

if __name__ == "__main__":

    executor = concurrent.futures.ThreadPoolExecutor(MAX_CONNECTIONS)

    while True:  
        connection_socket, client_addr = server_socket.accept()
        executor.submit(serve_connection, connection_socket, client_addr)
        
    server_socket.close()