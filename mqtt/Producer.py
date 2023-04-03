import os
import paho.mqtt.client as paho

from threading import Thread
from paho import mqtt
from constants import constant
from constants.constant import END_GAME


class Producer(Thread):
    def __init__(self, queue, topic, has_logout):
        super().__init__()
        self.queue = queue
        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set("cg4002", "password")
        self.client.max_inflight_messages_set(constant.MAX_INFLIGHT)
        self.client.connect(constant.MESSAGE_QUEUE_URL, 8883, 3600)
        self.topic = topic
        self.has_logout = has_logout

    def run(self):
        while True:
            action = self.queue.get()
            if action == END_GAME:
                break
            print(self.client.publish(self.topic, payload=action, qos=1))
        print("publisher disconnects")
