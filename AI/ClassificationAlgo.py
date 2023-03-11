from pynq import Overlay, allocate
from constants.Actions import Action
from AI.StartIdentification import *

mappedAction = {0: Action.SHIELD, 1: Action.GRENADE, 2: Action.RELOAD, 3: Action.LOGOUT}
overlay = Overlay('design_3_wrapper.bit')

def classifyMove(flattenedRow):
    dma = overlay.axi_dma_0
    input_buffer = allocate(shape=(108,), dtype=np.float32)
    output_buffer = allocate(shape=(1,), dtype=np.float32)
    for x, n in enumerate(flattenedRow):
        input_buffer[x] = n
    dma.sendchannel.transfer(input_buffer)
    dma.recvchannel.transfer(output_buffer)
    dma.sendchannel.wait()
    dma.recvchannel.wait()
    action = int(output_buffer)
    return action

def find_consecutive_num(arr):
    curr_num = None
    curr_count = 0
    for num in arr:
        if num == curr_num:
            curr_count += 1
            if curr_count == 5:
                return num
        else:
            curr_num = num
            curr_count = 1
    return 3  # no action


def getSlidingWindows(readings):
    result = []
    for i in range(0, len(readings) - 18 + 1, 1):
        result.append(readings[i:i + 6])
    return result


def flattenWindows(readings):
    sliding_windows = getSlidingWindows(readings)
    return [np.ravel(x) for x in sliding_windows]


def predict(readings):
    flattenedRows = flattenWindows(readings)
    list_of_actions = [classifyMove(flattenedRow) for flattenedRow in flattenedRows]
    predicted_action = mappedAction[find_consecutive_num(list_of_actions)]
    print("predict action: " + str(predicted_action.value))
    return predicted_action

if __name__ == "__main__":
    data=input()
    print(predict(data))
