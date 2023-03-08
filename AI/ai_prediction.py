from ClassificationAlgo import predict
from StartIdentification import *
import relay.relay_server as rs
from constants.Actions import Action

lock = rs.lock
rlok = rs.rlok
wlok = rs.wlok
flag = False


def process_data(action_queue):
    global flag
    rlok.acquire()
    if not flag and len(rs.cached_data) >= 10:
        flag = detect_move(rs.cached_data[0:10], window_size, slide_size)
    rlok.release()
    wlok.acquire()
    if len(rs.cached_data) >= 50:
        if flag:
            data = rs.cached_data[0:50]
        rs.cached_data = rs.cached_data[50:]
    wlok.release()
    if flag:
        predicted_result = predict(data)
        print("predicted action: " + str(predicted_result))
        action_queue.put(Action(predicted_result))
        flag = False


def start_ai(action_queue):
    process_data(action_queue)
