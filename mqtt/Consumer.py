import json
import paho.mqtt.client as paho
from threading import Thread
from paho import mqtt
from constants import constant


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
        self.client.username_pw_set("cg4002", "password")
        self.client.connect(constant.MESSAGE_QUEUE_URL, constant.MESSAGE_QUEUE_PORT_NUMBER)
        self.grenadeQuery_queue = queue
        self.has_logout = has_logout
        self.client.on_subscribe = on_subscribe
        self.client.on_message = self.on_message
        self.client.subscribe(constant.CONSUMER_TOPIC, qos=1)

    def on_message(self, client, userdata, msg):
        msg = msg.payload.decode("utf8")
        self.grenadeQuery_queue.put(json.loads(msg))

    def run(self):
        self.client.loop_start()
        self.has_logout[0].wait()
        self.has_logout[1].wait()
        self.client.loop_stop()
        print("consumer disconnects")
