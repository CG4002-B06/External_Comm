import socket

from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util.Padding import pad
from base64 import b64encode


class Eval_Client:

    def __init__(self, ip_addr, port_num):
        super().__init__()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip_addr, port_num)
        self.socket.connect(server_address)
        self.key = bytes("PLSPLSPLSPLSWORK", encoding="utf8")

    def __encrypt(self, plain_text):
        encoded_text = plain_text.encode(encoding="utf8")
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        cipher_text = b64encode(iv + cipher.encrypt(pad(encoded_text, AES.block_size)))
        return cipher_text

    def send_and_receive(self, plain_text):
        encrypted_text = self.__encrypt(plain_text)
        length = str(len(encrypted_text))
        self.socket.sendall(length.encode("utf8") + b'_' + encrypted_text)
        print("send data to eval")


        receive_data_length = b''
        while not receive_data_length.endswith(b'_'):
            receive_data_length += self.socket.recv(1)

        receive_data_length = receive_data_length.decode("utf8")
        length = int(receive_data_length[:-1])

        data = b''
        while len(data) < length:
            data += self.socket.recv(length - len(data))

        msg = data.decode("utf8")
        print("receive data from eval server: " + msg)
        return msg
