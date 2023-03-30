import os
import time
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
        remote_bind_address=('127.0.0.1', 6666),
        ssh_username='xilinx',
        ssh_password=xilinx_password,
        local_bind_address=('127.0.0.1', 6666),
        block_on_close=False
    )
    tunnel2.start()
    return tunnel2.local_bind_address


def run(data_queue, event, id):
    # add = start_tunnel()
    client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client1.connect(add)
    client1.connect(("localhost", 6674))
    client1.sendall(f'2_R{id}'.encode())
    event.wait()

    client1.sendall(b'1_B')
    client1.close()
