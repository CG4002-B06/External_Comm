from ClassificationAlgo import predict
from StartIdentification import *
import relay.relay_server as rs
from constants.Actions import Action

lk = rs.lk
event = rs.event


def start_prediction(action_queue):
    print("ai thread starts")
    while True:
        if event.is_set():
            print("event is set")
            lk.acquire()
            event.clear()
            data = rs.cached_data[0:100]
            rs.cached_data = rs.cached_data[100:]
            lk.release()
            print(data)
            
            #if detect_move(data[0:10], window_size, slide_size):
            predicted_result = predict(data)
            print("predicted action: " + str(predicted_result))
            action_queue.put(Action(predicted_result))
