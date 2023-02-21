import json

from .Player import *
from threading import Thread
from utils.player_utils import *


class GameEngine(Thread):
    def __init__(self, eval_client, action_queues, visualizer_queue, grenadeQuery_queue):
        super().__init__()
        self.players = [Player("p1"), Player("p2")]
        self.action_queues = action_queues
        self.visualizer_queue = visualizer_queue
        self.eval_client = eval_client
        self.grenadeQuery_queue = grenadeQuery_queue
        self.players[0].set_opponent(self.players[1])
        self.players[1].set_opponent(self.players[0])

    def run(self):
        while True:
            player1_object = {
                "action": self.action_queues[0].get()
            }
            player2_object = {
                "action": self.action_queues[1].get()
            }

            player1_action_check_result = self.players[0].check_valid_action(Action(player1_object.get("action")))
            player2_action_check_result = self.players[1].check_valid_action(Action(player2_object.get("action")))

            if player1_action_check_result:
                player1_object["invalid_action"] = player1_action_check_result
            elif player1_object.get("action") != Action.GRENADE.value:
                player1_object.update(self.players[0].get_status())
                self.players[0].process_action(player2_object.get("action"), {"p1": True})

            if player2_action_check_result:
                player2_object["invalid_action"] = player2_action_check_result
            elif player2_object.get("action") != Action.GRENADE.value:
                player2_object.update(self.players[1].get_status())
                self.players[1].process_action(player2_object.get("action"), {"p2": True})

            self.__send_normal_packet(player1_object, player2_object)

            query_result = {}
            if player1_object.get("action") == Action.GRENADE.value:
                query_result += self.grenadeQuery_queue.get()
            if player2_object.get("action") == Action.GRENADE.value:
                query_result += self.grenadeQuery_queue.get()

            if not player1_action_check_result and player1_object.get("action") == Action.GRENADE.value:
                self.players[0].process_action(player1_object.get("action"), query_result)
            if not player2_action_check_result and player2_object.get("action") == Action.GRENADE.value:
                self.players[1].process_action(player2_object.get("action"), query_result)

            # Store correct status from eval server into expected_status
            expected_status = json.loads(self.eval_client.send_and_receive(self.__build_eval_payload()))
            if status_has_discrepancy(self.players[0], expected_status.get("p1")) or \
                    status_has_discrepancy(self.players[1], expected_status.get("p2")):
                self.__correct_status(expected_status)
                self.__send_correction_packet(expected_status)
            elif player1_object.get("action") == Action.GRENADE.value or player2_object.get("action") == Action.GRENADE.value:
                self.__send_normal_packet(expected_status.get("p1"), expected_status.get("p2"))

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
                "grenades": expected_status.get("p1").get("grenades"),
                "shield_time": expected_status.get("p1").get("shield_time"),
                "num_deaths": expected_status.get("p1").get("num_deaths"),
                "num_shield": expected_status.get("p1").get("num_shield"),
                "bullets": expected_status.get("p1").get("bullets"),
                "shield_health": expected_status.get("p1").get("shield_health"),
                "num_of_death": expected_status.get("p1").get("num_deaths"),
                "num_of_shield": expected_status.get("p1").get("num_shield")    
            },
            "p2": {
                "hp": expected_status.get("p2").get("hp"),
                "grenades": expected_status.get("p2").get("grenades"),
                "shield_time": expected_status.get("p2").get("shield_time"),
                "num_deaths": expected_status.get("p2").get("num_deaths"),
                "num_shield": expected_status.get("p2").get("num_shield"),
                "bullets": expected_status.get("p2").get("bullets"),
                "shield_health": expected_status.get("p2").get("shield_health"),
                "num_of_death": expected_status.get("p2").get("num_deaths"),
                "num_of_shield": expected_status.get("p2").get("num_shield")             
            }
        }

        if error:
            message["error"] = error

        self.visualizer_queue.put(json.dumps(message))

    def __send_normal_packet(self, player1, player2, error=""):
        message = {
            "correction": False,
            "p1": player1,
            "p2": player2
        }

        if error:
            message["error"] = error

        self.visualizer_queue.put(json.dumps(message))

    def __correct_status(self, expected_status):
        self.players[0].correct_status(expected_status.get("p1"))
        self.players[1].correct_status(expected_status.get("p2"))

