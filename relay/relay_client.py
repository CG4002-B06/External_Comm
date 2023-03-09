import os
from socket import *
from threading import Thread

from dotenv import load_dotenv
import socket
import sshtunnel

load_dotenv()
username = os.getenv('SSH_TUNNEL_ID')
password = os.getenv('SSH_TUNNEL_PW')
xilinx_password = os.getenv('XINLINX_PW')
xilinx_ip = os.getenv('XINLINX_IP')


def start_tunnel():
    tunnel1 = sshtunnel.open_tunnel(
        ('stu.comp.nus.edu.sg', 22),
        remote_bind_address=(xilinx_ip, 22),
        ssh_username=username,
        ssh_password=password,
        block_on_close=False
    )
    tunnel1.start()
    tunnel2 = sshtunnel.open_tunnel(
        ssh_address_or_host=('localhost', tunnel1.local_bind_port),
        remote_bind_address=('127.0.0.1', 6667),
        ssh_username='xilinx',
        ssh_password=xilinx_password,
        local_bind_address=('127.0.0.1', 6667),
        block_on_close=False
    )
    tunnel2.start()
    return tunnel2.local_bind_address


def run(data_queue, response_queue, event):
    add = start_tunnel()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(add)

    while not event.is_set():
        data = data_queue.get()
        client.sendall(str(len(data)).encode("utf8") + b'_' + data)
        if len(data) == 4:  # this packet requires a response
            response = client.recv(3)
            health = int(response.decode("utf8"))
            print(health)
            response_queue.put(health)



