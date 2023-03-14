import json
import os
from queue import Queue
from threading import Thread
import paho.mqtt.client as paho

from paho import mqtt
from constants import mqtt_constant
from dotenv import load_dotenv

load_dotenv()
mq_username="cg4002"
mq_password="password"


def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


class Consumer(Thread):
    def __init__(self, queue, has_logout):
        super().__init__()
        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.on_connect = on_connect
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set(mq_username, mq_password)
        self.client.connect(mqtt_constant.MESSAGE_QUEUE_URL, mqtt_constant.MESSAGE_QUEUE_PORT_NUMBER)
        self.grenadeQuery_queue = queue
        self.has_logout = has_logout

        self.client.on_subscribe = on_subscribe
        self.client.on_message = self.on_message

        self.client.subscribe(mqtt_constant.CONSUMER_TOPIC, qos=1)

    def on_message(self, client, userdata, msg):
        msg = msg.payload.decode("utf8")
        print(msg)
        self.grenadeQuery_queue.put(json.loads(msg))

    def run(self):
        print("start subscribing data from HiveMQ")
        self.client.loop_start()
        while not (self.has_logout[0].is_set() and self.has_logout[1].is_set()):
            pass
        self.client.loop_stop()
        print("consumer disconnects")
