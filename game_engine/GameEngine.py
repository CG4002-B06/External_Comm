import json

from .Player import *
from threading import Thread
from utils.player_utils import *

class GameEngine(Thread):
    def __init__(self, action_queues, visualizer_queue, grenadeQuery_queue, relay_queue,
                 has_logout, is_one_player, eval_client=None):
        super().__init__()
        self.action_queues = action_queues
        self.visualizer_queue = visualizer_queue
        self.eval_client = eval_client
        self.grenadeQuery_queue = grenadeQuery_queue
        self.is_one_player = is_one_player
        self.has_logout = has_logout
        self.players = [Player("p1", relay_queue, self.has_logout[0]), Player("p2", relay_queue, self.has_logout[1])]
        self.players[0].set_opponent(self.players[1])
        self.players[1].set_opponent(self.players[0])

    def run(self):
        while not (self.has_logout[0].is_set() and self.has_logout[1].is_set()):
            query_result = {}
            [action1, query1] = self.action_queues[0].get()
            if not self.is_one_player:
                [action2, query2] = self.action_queues[1].get()
            else:
                [action2, query2] = [Action.NONE, {}]
            query_result.update(query1)
            query_result.update(query2)

            # query for grenade result (if needed)
            grenades = 0
            if action1 == Action.GRENADE:
                self.__send_query_packet("p1")
                grenades += 1
            if action2 == Action.GRENADE:
                self.__send_query_packet("p2")
                grenades += 1
            
            for i in range(0, grenades):
                grenade_result = self.grenadeQuery_queue.get()
                query_result = {
                    "p1" : query_result.get("p1") or grenade_result.get("p1"),
                    "p2": query_result.get("p2") or grenade_result.get("p2")
                }

            player_object1 = self.__build_player_object(0, action1, query_result)
            player_object2 = self.__build_player_object(1, action2, query_result)

            # check against eval server
            if self.eval_client is not None:
                expected_status = json.loads(self.eval_client.send_and_receive(self.__build_eval_payload()))
                # if status mismatches, send correction packet
                if status_has_discrepancy(self.players[0], expected_status.get("p1")) or \
                        status_has_discrepancy(self.players[1], expected_status.get("p2")):
                    self.__correct_status(expected_status)
                    self.__send_correction_packet()
                    continue

            self.__send_normal_packet(player_object1, player_object2)
        print("game engine exits")

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

        self.visualizer_queue.put(json.dumps(message))

    def __build_player_object(self, player_id, action, query_result):
        check_result = self.players[player_id].check_action(action)
        player_object = {"action": action.value, "isHit": query_result.get("p" + str(player_id + 1), True)}
        if not check_result:
            self.players[player_id].process_action(action, query_result)
        else:
            player_object["invalid"] = check_result

        player_object.update(self.players[player_id].get_status())
        return player_object

    def __send_normal_packet(self, player1, player2):
        message = {
            "correction": False,
            "p1": player1,
            "p2": player2
        }

        self.visualizer_queue.put(json.dumps(message))

    def __send_query_packet(self, player_id):
        message = {
            "correction": False,
            "p1": {
                "action": Action.NONE.value
            },
            "p2": {
                "action": Action.NONE.value
            },
            player_id: {
                "action": Action.GRENADE.value
            }
        }

        self.visualizer_queue.put(json.dumps(message))

    def __correct_status(self, expected_status):
        self.players[0].correct_status(expected_status.get("p1"))
        self.players[1].correct_status(expected_status.get("p2"))
