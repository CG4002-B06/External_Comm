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
    client1.sendall(f'H{id}'.encode())

    time.sleep(6)
    client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2.connect(("localhost", 6674))
    # client2.connect(add)
    t = Thread(target=receive_health_change, args=(client2, event))
    t.start()

    while not event.is_set():
        data = data_queue.get()
        if data == "logout":
            break
        client1.sendall(str(len(data)).encode("utf8") + b'_' + data)
    client1.close()


def receive_health_change(socket, event):
    while not event.is_set():
        while True:
            data = b''
            while not data.endswith(b'_'):
                _d = socket.recv(1)
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
                _d = socket.recv(length - len(data))
                if not _d:
                    data = b''
                    continue
                data += _d
            if len(data) == 0:
                print('no more data from the client')
                break
            response = eval(data.decode())
            print(response)
            if response.get("p1").get("action") == "logout":
                socket.close()
                return

        # health1, health2 = response.get("p1"), response.get("p2")
        # if health1:
        #     health1 = int(health1)
        # if health2:
        #     health2 = int(health2)
        # print("p1 health: " + str(health1))
        # print("p2 health: " + str(health2))
