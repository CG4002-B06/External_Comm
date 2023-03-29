import json
from AI.ClassificationAlgo import predict
import relay.relay_server as rs
from constants.Actions import Action
from constants import constant
import csv

class bcolors:
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def start_prediction(action_queue, event_queue, has_logout, id):
    lk = rs.lk[id]
    queue_full = rs.queue_full[id]
    # action = 'shield'
    # counter = 810

    while not has_logout.is_set():
        queue_full.wait()
        lk.acquire()
        data = rs.cached_data[id][0:constant.ROW_SIZE]
        rs.cached_data[id] = rs.cached_data[id][constant.ROW_SIZE:]
        queue_full.clear()
        lk.release()

        # filename = f"{action}_{id}_{counter}.csv"
        # with open(filename, 'w', newline='') as csvfile:
        #     writer = csv.writer(csvfile)
        #
        #     for row in data:
        #         writer.writerow(row)
        # if id == 0:
        #     print(f"{bcolors.OKBLUE}{bcolors.BOLD}Write {counter}{bcolors.ENDC}")
        #     print(f"{bcolors.OKBLUE}{bcolors.BOLD}{data}{bcolors.ENDC}")
        # else:
        #     print(f"{bcolors.OKGREEN}{bcolors.BOLD}Write {counter}{bcolors.ENDC}")
        #     print(f"{bcolors.OKGREEN}{bcolors.BOLD}{data}{bcolors.ENDC}")
        # counter += 1

        predicted_result = predict(data)
        if id == 0:
            print(f"{bcolors.OKBLUE}{bcolors.BOLD}{predicted_result}{bcolors.ENDC}")
        else:
            print(f"{bcolors.OKGREEN}{bcolors.BOLD}{predicted_result}{bcolors.ENDC}")
        if predicted_result == Action.NONE:
            event_queue.put(json.dumps({
                "p1": None, "p2": None,
                f"p{id + 1}": constant.REDO_ACTION_MSG
                }))
        else:
            action_queue.put([Action(predicted_result), {}])
