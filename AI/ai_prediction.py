from AI.ClassificationAlgo import predict
import relay.relay_server as rs
from constants.Actions import Action
from constants import ai_constant
import csv


def start_prediction(action_queue, has_logout, id):
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

        # TODO: needs to publish None to visualizer and asks players to repeat
        if predicted_result != Action.NONE:
            action_queue.put([Action(predicted_result), {}])
