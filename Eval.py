import socket
import hashlib

from threading import Thread
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util.Padding import pad
from base64 import b64encode

class Eval(Thread):

    def __init__(self, ip_addr, port_num, eval_queue, main_thread_queue):
        super().__init__()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip_addr, port_num)
        self.socket.connect(server_address)

        self.eval_queue = eval_queue
        self.main_thread_queue = main_thread_queue
        self.key = bytes("PLSPLSPLSPLSWORK", encoding="utf8")

    def __encrypt(self, plain_text):
        encoded_text = plain_text.encode(encoding="utf8")
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        cipher_text = b64encode(iv + cipher.encrypt(pad(text, AES.block_size)))
        return cipher_text

    def __send(self, plain_text):
        encrypted_text = self.__encrypt(plain_text)
        received = self.socket.sendall(encrypted_text)
        return received
       
    
    def run(self):
        while True:
            data = self.eval_queue.get()
            sent_hash_value = hashlib.sha1(byte(data, "utf8")).hexdigest()
            
            received_data = self.__send(data) # send data to eval server for checking
            
            received_hash_value = hashlib.sha1(byte(received_data, "utf8")).hexdigest()
            if (sent_hash_value != received_hash_value):
                self.main_thread_queue.put(received)