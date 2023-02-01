from sshtunnel import SSHTunnelForwarder
import os
from socket import *
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('SSH_TUNNEL_ID')
password = os.getenv('SSH_TUNNEL_PW')
xilinx_password = os.getenv('XINLINX_PW')

server = SSHTunnelForwarder(
    ssh_address=('stu.comp.nus.edu.sg', 22),
    ssh_username=username,
    ssh_password=password,
    remote_bind_address=('192.168.95.222', 6666),
    local_bind_address=('localhost', 6667)
)

server.start()
print("started")
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(('192.168.95.222', 6666))
user_input = input()
client_socket.sendall(user_input.encode("utf8"))

print('FINISH!')
server.stop()
