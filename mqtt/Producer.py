import os
import paho.mqtt.client as paho

from threading import Thread
from paho import mqtt
from constants import mqtt_constant

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
        self.client.username_pw_set(mq_username, mq_password)
        self.client.connect(mqtt_constant.MESSAGE_QUEUE_URL, 8883)


    def run(self):
        print("start publishing data to HiveMQ")
        while True:
            action = self.queue.get()
            self.client.publish(mqtt_constant.PUBLISH_TOPIC, payload=action, qos=2)

