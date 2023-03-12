import os
import paho.mqtt.client as paho

from threading import Thread
from paho import mqtt
from constants import mqtt_constant

from dotenv import load_dotenv

load_dotenv()

mq_username="cg4002"
mq_password="password"

class Producer(Thread):
    def __init__(self, queue, topic):
        super().__init__()
        self.queue = queue
        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set("cg4002", "password")
        self.client.max_inflight_messages_set(mqtt_constant.MAX_INFLIGHT)
        self.client.connect(mqtt_constant.MESSAGE_QUEUE_URL, 8883)
        self.topic = topic

    def run(self):
        print("start publishing data to HiveMQ")
        while True:
            action = self.queue.get()
            self.client.publish(self.topic, payload=action, qos=1)
            print("published message: " + str(action))
