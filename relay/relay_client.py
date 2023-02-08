import os
from socket import *
from dotenv import load_dotenv
import socket
import threading
import sshtunnel

load_dotenv()
username = os.getenv('SSH_TUNNEL_ID')
password = os.getenv('SSH_TUNNEL_PW')
xilinx_password = os.getenv('XINLINX_PW')
xilinx_ip = os.getenv('XINLINX_IP')


# connecting to ultra96
class UltraClient(threading.Thread):
    def __init__(self):
        super().__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # sshtunneling into sunfire
    def start_tunnel(self):
        tunnel1 = sshtunnel.open_tunnel(
            ('stu.comp.nus.edu.sg', 22),
            remote_bind_address=(xilinx_ip, 22),
            ssh_username=username,
            ssh_password=password,
            block_on_close=False
        )
        tunnel1.start()

        print('[Tunnel Opened] Tunnel into Sunfire: ' + str(tunnel1.local_bind_port))

        tunnel2 = sshtunnel.open_tunnel(
            ssh_address_or_host=('localhost', tunnel1.local_bind_port),
            remote_bind_address=('127.0.0.1', 6666),
            ssh_username='xilinx',
            ssh_password=xilinx_password,
            local_bind_address=('127.0.0.1', 6666),
            block_on_close=False
        )
        tunnel2.start()
        print('[Tunnel Opened] Tunnel into Xilinx')

        return tunnel2.local_bind_address

    def run(self):
        # add = self.start_tunnel()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.client.connect(add)
        self.client.connect(('localhost', 6666))
        print("[ULTRA96 CONNECTED] Connected to Ultra96")

        while True:
            data = input("Some dummy data here: ")
            if data == "stop":
                break
            self.client.sendall(data.encode("utf8"))
        self.client.close()
        print("[CLOSED]")
