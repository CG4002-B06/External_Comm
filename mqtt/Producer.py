import os
import paho.mqtt.client as paho

from threading import Thread
from paho import mqtt
from constants import constant

class Producer(Thread):
    def __init__(self, queue, topic, has_logout):
        super().__init__()
        self.queue = queue
        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set("cg4002", "password")
        self.client.max_inflight_messages_set(constant.MAX_INFLIGHT)
        self.client.connect(constant.MESSAGE_QUEUE_URL, 8883)
        self.topic = topic
        self.has_logout = has_logout

    def run(self):
        while not (self.has_logout[0].is_set() and self.has_logout[1].is_set()):
            action = self.queue.get()
            result = self.client.publish(self.topic, payload=action, qos=1)
            print("publish result: " + str(result.rc))
        print("publisher disconnects")
