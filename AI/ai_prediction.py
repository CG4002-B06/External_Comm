import json

from AI.ClassificationAlgo import predict
import relay.relay_server as rs
from constants.Actions import Action
from constants import ai_constant, player_constant
import csv


def start_prediction(action_queue, event_queue, has_logout, id):
    lk = rs.lk[id]
    queue_full = rs.queue_full[id]

    while not has_logout.is_set():
        queue_full.wait()
        lk.acquire()
        data = rs.cached_data[id][0:ai_constant.ROW_SIZE]
        rs.cached_data[id] = rs.cached_data[id][ai_constant.ROW_SIZE:]
        queue_full.clear()
        lk.release()
        predicted_result = predict(data)

        if predicted_result == Action.NONE:
            event_queue.put(json.dumps({
                "p1": None, "p2": None,
                f"p{id + 1}": player_constant.REDO_ACTION_MSG
            }))
        else:
            action_queue.put([Action(predicted_result), {}])
