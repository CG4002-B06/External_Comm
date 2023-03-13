from pynq import Overlay, allocate
from constants.Actions import Action
from AI.StartIdentification import *

mappedAction = {0: Action.SHIELD, 1: Action.GRENADE, 2: Action.RELOAD, 3: Action.LOGOUT}
overlay = Overlay('design_4_wrapper.bit')

def classifyMove(flattenedRow):
    dma = overlay.axi_dma_0
    input_buffer = allocate(shape=(120,), dtype=np.float32)
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
    print(arr)
    for num in arr:
        if num == curr_num:
            curr_count += 1
            if curr_count > 0:
                return num
        else:
            curr_num = num
            curr_count = 1
    return 3  # no action


def getSlidingWindows(readings):
    result = []
    for i in range(0, len(readings) - 75 + 1, 1):
        result.append(readings[i:i + 6])
    return result


def flattenWindows(readings):
    sliding_windows = getSlidingWindows(readings)
    return [np.ravel(x) for x in sliding_windows]


def predict(readings):
    flattenedRows = flattenWindows(readings)
    list_of_actions = [classifyMove(flattenedRow) for flattenedRow in flattenedRows]
    predicted_action = mappedAction[find_consecutive_num(list_of_actions)]
    # predicted_action = find_consecutive_num(list_of_actions)
    print("predict action: " + str(predicted_action))
    return predicted_action

if __name__ == "__main__":
    #data=[[-6048, -17884, 31004, 17551, -1398, 9892], [-2236, -25892, 20580, -10032, -4719, 1830], [-6256, -16924, 7676, -32768, -12676, 23145], [-12496, -8972, 3488, -25543, -7052, 32767], [-13644, -996, 8916, -9644, -9613, 32767], [-9136, -500, 14164, -3210, -16900, 24811], [-5480, 4292, 19312, 2392, 1, 17143], [-1548, 3012, 18104, 2030, -2990, 14144], [-620, 968, 18712, -587, -6089, 5335], [2552, 624, 18692, -1979, -529, -1328], [3388, 608, 18080, -263, -617, -1367], [2292, 628, 19572, -609, -499, 52], [-4996, 3080, 20368, -9972, 10376, -20014], [-19236, 548, 14020, 10524, 32767, -32768], [-14240, -1976, -16, 28637, 25037, -32724], [-4828, -6972, -740, 32767, 9000, -10939], [1408, -15560, 5056, 32767, 4237, 2015], [-1560, -18132, 17232, 32767, 3036, 7242], [-3380, -23304, 27296, 1662, 1686, -3292], [-748, -32768, 15364, -1564, -476, -823]]
    print(predict(data))
