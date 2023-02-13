import os
import paho.mqtt.client as paho

from threading import Thread
from paho import mqtt
from constants import producer_constant
from dotenv import load_dotenv

load_dotenv()
mq_username = os.getenv('MESSAGE_QUEUE_USERNAME')
mq_password = os.getenv('MESSAGE_QUEUE_PW')


class Producer(Thread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set("cg4002", "password")
        self.client.connect("01f054988a0f4d7ea2bbe9aaa0b080f7.s2.eu.hivemq.cloud", 8883)

    def run(self):
        print("start publishing data to HiveMQ")
        while True:
            action = self.queue.get()
            print("receive action data: " + action)
            self.client.publish("Player", payload=action, qos=2)
            # self.client.publish(producer_constant.TOPIC2, payload=action, qos=2)
