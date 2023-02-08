import json
import copy

from .Player import *
from threading import Thread
from constants.Actions import Action
from utils.player_utils import *


def process(actions, players):
    result = [None] * 2
    for i in range(0, len(actions)):
        action = actions[i].get("action")
        result[i] = players[i].process_action(action)
    return result


class GameEngine(Thread):
    def __init__(self, eval_client, action_queue, visualizer_queue):
        super().__init__()
        self.players = [Player(), Player()]
        self.action_queue = action_queue
        self.visualizer_queue = visualizer_queue
        self.eval_client = eval_client
        self.players[0].set_opponent(self.players[1])
        self.players[1].set_opponent(self.players[0])

    def run(self):
        while True:
            # actions = [self.action_queue.get()]
            action = self.action_queue.get()
            print("engine gets data: " + action)
            actions = [
                {
                    "action": action,
                    "player": 0
                },
                {
                    "action": Action.NONE.value,
                    "player": 1
                }
            ]
            # if self.action_queue.qsize() > 0 and self.action_queue[0].get("player") != actions[0].get("player"):
            #     actions.append(self.action_queue.get())
            # else:
            #     actions.append({
            #         "action": Action.NONE.value,
            #         "player": (actions[0].get("player") + 1) % 2
            #     })
            actions.sort(key=lambda x: x.get("player"))
            players_copy = copy.deepcopy(self.players)
            process_result = process(actions, self.players)

            expected_status = json.loads(self.eval_client.send_and_receive(self.__build_eval_payload()))
            expected_actions = [{"action": expected_status.get("p1").get("action"), "player": 0},
                                {"action": expected_status.get("p2").get("action"), "player": 1}]

            if actions == expected_actions:
                if status_has_discrepancy(self.players[0], expected_status.get("p1")) or \
                        status_has_discrepancy(self.players[1], expected_status.get("p2")):
                    self.__correct_status(expected_status)
                    self.__send_correction_packet(expected_status)
                else:
                    self.__send_normal_packet(process_result)
            else:
                reprocess_result = process(expected_actions, players_copy)
                if status_has_discrepancy(players_copy[0], expected_status.get("p1")) or \
                        status_has_discrepancy(self.players[1], expected_status.get("p2")):
                    self.__correct_status(expected_status)
                    self.__send_correction_packet(expected_status)
                else:
                    self.players = players_copy
                    self.__send_normal_packet(reprocess_result)

    def __build_eval_payload(self):
        payload = {
            "p1": self.players[0].get_status(),
            "p2": self.players[1].get_status()
        }
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
                "shield_health": expected_status.get("p1").get("shield_health")
            },
            "p2": {
                "hp": expected_status.get("p2").get("hp"),
                "grenade": expected_status.get("p2").get("grenades"),
                "shield": expected_status.get("p2").get("num_shield"),
                "num_of_death": expected_status.get("p2").get("num_deaths"),
                "num_of_shield": expected_status.get("p2").get("num_shield"),
                "bullet": expected_status.get("p2").get("bullets"),
                "shield_health": expected_status.get("p2").get("shield_health")
            }
        }

        if error:
            message["error"] = error

        self.visualizer_queue.put(json.dumps(message))

    def __send_normal_packet(self, result, error=""):
        message = {
            "correction": False,
            "p1": json.dumps(result[0]),
            "p2": json.dumps(result[1])
        }

        if error:
            message["error"] = error

        self.visualizer_queue.put(json.dumps(message))

    def __correct_status(self, expected_status):
        print("correct players status....")
        self.players[0].correct_status(expected_status.get("p1"))
        self.players[1].correct_status(expected_status.get("p2"))
