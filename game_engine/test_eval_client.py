from game_engine.eval_client import Eval_Client
import json

if __name__ == "__main__":
    client = Eval_Client("localhost", 7001)
    input()
    data1 = {
        "p1": {
            "hp": 10,
            "action": "grenade",
            "bullets": 1,
            "grenades": 1,
            "shield_time": 0,
            "shield_health": 3,
            "num_deaths": 1,
            "num_shield": 0
        },
        "p2": {
            "hp": 100,
            "action": "shield",
            "bullets": 2,
            "grenades": 2,
            "shield_time": 1,
            "shield_health": 0,
            "num_deaths": 5,
            "num_shield": 2
        }
    }

    received_msg = client.send_and_receive(json.dumps(data1))
