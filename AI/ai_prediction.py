from AI.ClassificationAlgo import predict
from AI.StartIdentification import *
import keras
from keras.models import load_model
import relay.relay_server as rs
from constants.Actions import Action
from constants import ai_constant
import pandas as pd
lk = rs.lk
event = rs.event

model = load_model('my_model.h5')
def start_prediction(action_queue, has_logout):
    while not (has_logout[0].is_set() and has_logout[1].is_set()):
        event.wait()
        lk.acquire()
        event.clear()
        data = rs.cached_data[0:ai_constant.ROW_SIZE]
        rs.cached_data = rs.cached_data[ai_constant.ROW_SIZE:]
        if len(rs.cached_data) < ai_constant.ROW_SIZE:
            rs.cached_data = []
        lk.release()

        # flag = detect_move(pd.DataFrame(data[0:ai_constant.DETECT_MOVE_SIZE]), window_size, slide_size)
        # print("flag: " + str(flag))
        # if flag:
        #     predicted_result = predict(data)
        predicted_result = model.predict(data)
        action_queue.put([Action(predicted_result), {}])
