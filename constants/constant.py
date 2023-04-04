# EVAL SERVER CONSTANT
# IP_ADDRESS = "137.132.92.184"
IP_ADDRESS="localhost"
PORT_NUMBER = 7001

# Game Prompt
RELOAD_ERROR_MESSAGE = "Warning! \n\n Unable to reload as you still have ammo"
SHOOT_ERROR_MESSAGE = "Warning! \n\n You are out of ammo"
GRENADE_ERROR_MESSAGE = "Warning! \n\n You are out of grenades"
SHIELD_ERROR_MESSAGE = "Warning! \n\n You are out of shields"
SHIELD_COOLDOWN_MESSAGE = "Warning! \n\n Shield on cooldown"
TARGET_VIEW_ERROR_MESSAGE = "Miss! Target not found."

WAIT_SENSOR_INIT_MESSAGE = "DONT MOVE GLOVE! \n SENSORS ARE INITIALISING..."
INIT_COMPLETE_MSG = "SENSORS HAVE BEEN INITIALISED \n ENJOY SHOOTING!"
REDO_ACTION_MSG = "ACTION UNDETECTED! \n REDO ACTION"
SENSOR_DISCONNECT_MSG = "CONNECTION LOST \n GET CLOSER TO THE RELAY NODE"
SENSOR_RECONNECT_MSG = "CONNECTION RE-ESTABLISHED"


# MQTT CONSTANTS
MESSAGE_QUEUE_URL = "c3cdb3543d864e04ab578cac5a022296.s1.eu.hivemq.cloud"
# MESSAGE_QUEUE_URL="01f054988a0f4d7ea2bbe9aaa0b080f7.s2.eu.hivemq.cloud"
MESSAGE_QUEUE_PORT_NUMBER = 8883
PUBLISH_TOPIC_V = "Player"
PUBLISH_TOPIC_E = "Events"
CONSUMER_TOPIC = "QueryGrenade"
MAX_INFLIGHT = 9999

# Game State Constant
HAS_EVAL = True
ONE_PLAYER = False
END_GAME = "_GAME_ENDING_"

# AI CONSTANT
ROW_SIZE = 20

