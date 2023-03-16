from AI.ClassificationAlgo import predict
from AI.StartIdentification import *
import relay.relay_server as rs
from constants.Actions import Action
from constants import ai_constant
import pandas as pd
import csv
lk = rs.lk
event = rs.event

def start_prediction(action_queue, has_logout):
    while not (has_logout[0].is_set() and has_logout[1].is_set()):
        while True:
            lk.acquire()
            if len(rs.cached_data) >= ai_constant.ROW_SIZE:
                break
            lk.release()
        
        data = rs.cached_data[0:ai_constant.ROW_SIZE]
        print(data)
        rs.cached_data = rs.cached_data[ai_constant.ROW_SIZE:]
        lk.release()
        predicted_result = predict(data)
        if predicted_result != Action.NONE:
            action_queue.put([Action(predicted_result), {}])
