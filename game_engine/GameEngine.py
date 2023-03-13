import json

from .Player import *
from threading import Thread
from utils.player_utils import *


class GameEngine(Thread):
    def __init__(self, action_queues, visualizer_queue, grenadeQuery_queue, hp_queue, is_one_player, eval_client=None):
        super().__init__()
        self.players = [Player("p1", hp_queue), Player("p2", hp_queue)]
        self.action_queues = action_queues
        self.visualizer_queue = visualizer_queue
        self.eval_client = eval_client
        self.grenadeQuery_queue = grenadeQuery_queue
        self.players[0].set_opponent(self.players[1])
        self.players[1].set_opponent(self.players[0])
        self.is_one_player = is_one_player


    def run(self):
        while True:
            [action1, query1] = self.action_queues[1].get()
            if not self.is_one_player:
                [action2, query2] = self.action_queues[0].get()
            else:
                [action2, query2] = [Action.NONE, {}]

            print(action1)
            print(query1)
            # check validness of player actions and build the json payload
            # process and update status if action is not grenade
            player_object1, valid_action1 = self.__build_player_object(0, action1, query1)
            player_object2, valid_action2 = self.__build_player_object(1, action2, query2)
            self.__send_normal_packet(player_object1, player_object2)

            # if any of action is grenade, retrieve query response and update status
            query_result = {}
            if action1.value == Action.GRENADE.value and valid_action1:
                query_result.update(self.grenadeQuery_queue.get())
                self.players[0].process_action(action1, query_result)
                player_object1 = self.players[0].get_status(False)

            if action2.value == Action.GRENADE.value and valid_action2:
                query_result.update(self.grenadeQuery_queue.get())
                self.players[1].process_action(action2, query_result)
                player_object2 = self.players[1].get_status(False)
            if self.eval_client is not None:
                # check against the eval server
                expected_status = json.loads(self.eval_client.send_and_receive(self.__build_eval_payload()))
                # if status mismatches, send correction packet
                if status_has_discrepancy(self.players[0], expected_status.get("p1")) or \
                        status_has_discrepancy(self.players[1], expected_status.get("p2")):
                    self.__correct_status(expected_status)
                    self.__send_correction_packet()
                    continue
            # if any of action is grenade, need to send post-update status to visualizer for UI update
            if Action.GRENADE.value in [action1.value, action2.value]:
                self.__send_normal_packet(player_object1, player_object2)


    def __build_eval_payload(self):
        payload = {
            "p1": self.players[0].get_status(),
            "p2": self.players[1].get_status()
        }
        return json.dumps(payload)

    def __send_correction_packet(self, error=""):
        message = {
            "correction": True,
            "p1": self.players[0].get_status(need_shield_time=False),
            "p2": self.players[1].get_status(need_shield_time=False),
        }

        if error:
            message["error"] = error

        self.visualizer_queue.put(json.dumps(message))

    def __build_player_object(self, player_id, action, query_result):
        player_object = {"action": action.value}
        check_result = self.players[player_id].check_action(action)
        if not check_result and action.value != Action.GRENADE.value:
            self.players[player_id].process_action(action, query_result)
        if action.value != Action.GRENADE.value:
            player_object.update(self.players[player_id].get_status())
            if action.value == Action.SHOOT.value:
                player_object.update({"isHit": query_result.get("p" + str(player_id + 1))})

        if check_result:
            player_object["invalid"] = check_result
        return player_object, check_result is None

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