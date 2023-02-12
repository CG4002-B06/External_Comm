import os
from queue import Queue
from threading import Thread
import paho.mqtt.client as paho

from paho import mqtt
from constants import mqtt_constant
from dotenv import load_dotenv

load_dotenv()
mq_username = os.getenv('MESSAGE_QUEUE_USERNAME')
mq_password = os.getenv('MESSAGE_QUEUE_PW')

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
class Consumer(Thread):
    def __init__(self, queue):
        super().__init__()
        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.on_connect = on_connect
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set("consumer", "consumer")
        self.client.connect(mqtt_constant.MESSAGE_QUEUE_URL, mqtt_constant.MESSAGE_QUEUE_PORT_NUMBER)

        # setting callbacks, use separate functions like above for better visibility
        self.client.on_subscribe = on_subscribe
        self.client.on_message = on_message

        self.client.subscribe("test", qos=1)

    def run(self):
        print("start subscribing data from HiveMQ")
        print(self.client)
        self.client.loop_forever()


if __name__ == "__main__":
    q = Queue()
    Consumer(q).start()
