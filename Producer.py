from threading import Thread
import paho.mqtt.client as paho
from paho import mqtt

class Producer(Thread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set("producer", "producer")
        self.client.connect("c3cdb3543d864e04ab578cac5a022296.s1.eu.hivemq.cloud", 8883)

    def run(self):
        print("start publishing data to HiveMQ")
        while True:
            action = self.queue.get()
            print("receive action data: " + action)
            self.client.publish("p/player1", payload=action, qos=2)
            self.client.publish("publisher/player2", payload=action, qos=2)
        print("stop")
