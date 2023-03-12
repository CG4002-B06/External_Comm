from AI.ClassificationAlgo import predict
from AI.StartIdentification import *
import relay.relay_server as rs
from constants.Actions import Action
from constants import ai_constant
import pandas as pd
lk = rs.lk
event = rs.event


def start_prediction(action_queue):
    while True:
        event.wait()
        lk.acquire()
        event.clear()
        data = rs.cached_data[0:ai_constant.ROW_SIZE]
        rs.cached_data = rs.cached_data[ai_constant.ROW_SIZE:]
        lk.release()

        flag = detect_move(pd.DataFrame(data[0:ai_constant.DETECT_MOVE_SIZE]), window_size, slide_size)
        print("flag: " + str(flag))
        if flag:
            print(data)
            predicted_result = predict(data)
            action_queue.put({Action(predicted_result), {}})
