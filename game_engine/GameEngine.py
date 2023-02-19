import json
import copy

from .Player import *
from threading import Thread
from constants.Actions import Action
from utils.player_utils import *


def process(actions, players):
    result = [None] * 2
    for i in range(0, 2):
        result[i] = players[i].process_action(actions[i])
    return result


class GameEngine(Thread):
    def __init__(self, eval_client, action_queues, visualizer_queue, grenadeQuery_queue):
        super().__init__()
        self.players = [Player(), Player()]
        self.action_queues = action_queues
        self.visualizer_queue = visualizer_queue
        self.eval_client = eval_client
        self.grenadeQuery_queue = grenadeQuery_queue
        self.players[0].set_opponent(self.players[1])
        self.players[1].set_opponent(self.players[0])

    def run(self):
        while True:
            actions = [self.action_queues[0].get(), self.action_queues[1].get()]
            print("\nengine gets data: " + str(actions))
            has_sent = False

            if actions[0] == Action.GRENADE.value or actions[1] == Action.GRENADE.value:
                has_sent = True

                self.__send_query_packet(actions[0], actions[1])
                response = self.grenadeQuery_queue.get()
                if actions[0] == Action.GRENADE:
                    self.players[0].process_grenade(response.get("p1"))
                else:
                    self.players[0].process_action(actions[0])

                if actions[1] == Action.GRENADE:
                    self.players[1].process_grenade(response.get("p2"))
                else:
                    self.players[1].process_action(actions[1])
            else:
                process_result = process(actions, self.players)

            expected_status = json.loads(self.eval_client.send_and_receive(self.__build_eval_payload()))
            if status_has_discrepancy(self.players[0], expected_status.get("p1")) or \
                    status_has_discrepancy(self.players[1], expected_status.get("p2")):
                self.__correct_status(expected_status)
                self.__send_correction_packet(expected_status)
            elif not has_sent:
                self.__send_normal_packet(process_result)

    def __build_eval_payload(self):
        payload = {
            "p1": self.players[0].get_status(),
            "p2": self.players[1].get_status()
        }
        print("\nprior to sending to eval server: \n" + str(payload))
        return json.dumps(payload)

    def __send_correction_packet(self, expected_status, error=""):
        message = {
            "correction": True,
            "p1": {
                "hp": expected_status.get("p1").get("hp"),
                "grenade": expected_status.get("p1").get("grenades"),
                "shield": expected_status.get("p1").get("num_shield"),
                "num_of_death": expected_status.get("p1").get("num_deaths"),
                "num_of_shield": expected_status.get("p1").get("num_shield"),
                "bullet": expected_status.get("p1").get("bullets"),
                "shield_health": expected_status.get("p1").get("shield_health"),
                "action": expected_status.get("p1").get("action")
            },
            "p2": {
                "hp": expected_status.get("p2").get("hp"),
                "grenade": expected_status.get("p2").get("grenades"),
                "shield": expected_status.get("p2").get("num_shield"),
                "num_of_death": expected_status.get("p2").get("num_deaths"),
                "num_of_shield": expected_status.get("p2").get("num_shield"),
                "bullet": expected_status.get("p2").get("bullets"),
                "shield_health": expected_status.get("p2").get("shield_health"),
                "action": expected_status.get("p2").get("action")
            }
        }

        if error:
            message["error"] = error

        self.visualizer_queue.put(json.dumps(message))

    def __send_normal_packet(self, result, error=""):
        message = {
            "correction": False,
            "p1": result[0],
            "p2": result[1]
        }

        if error:
            message["error"] = error

        self.visualizer_queue.put(json.dumps(message))

    def __send_query_packet(self, action1, action2, error=""):
        message = {
            "correction": False,
            "p1": {
                "action": action1
            },
            "p2": {
                "action": action2,
            }
        }

        if error:
            message["error"] = error

        self.visualizer_queue.put(json.dumps(message))

    def __correct_status(self, expected_status):
        print("correct players status....\n")
        self.players[0].correct_status(expected_status.get("p1"))
        self.players[1].correct_status(expected_status.get("p2"))
        print("after correcting the status...\n")
        print(self.players[0].get_status())
        print(self.players[1].get_status())
