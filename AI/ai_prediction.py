from ClassificationAlgo import predict
from StartIdentification import *
import relay.relay_server as rs
from constants.Actions import Action
import pandas as pd
lk = rs.lk
event = rs.event


def start_prediction(action_queue):
    print("ai thread starts")
    while True:
        event.wait()
        lk.acquire()
        event.clear()
        data = rs.cached_data[0:25]
        rs.cached_data = rs.cached_data[25:]
        lk.release()

        flag = detect_move(pd.DataFrame(data[0:10]), window_size, slide_size) 
        print("flag: " + str(flag))
        if flag:
            predicted_result = predict(data)
            action_queue.put(Action(predicted_result))
