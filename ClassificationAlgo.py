import pynq
import pynq.lib.dma
from pynq import Overlay, allocate
import pandas as pd
import time
import numpy as np


def classifyMove(flattenedRow):
    overlay = Overlay('design_1_wrapper.bit')
    dma = overlay.axi_dma_0
    input_buffer = allocate(shape=(150,), dtype=np.float32)
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
    return 3 #no action

def getSlidingWindows(readings):
    result = []
    for i in range(0, len(readings) - 25 + 1, 1):
        result.append(readings[i:i + 25])
    return result
    
def  flattenWindows():
    sliding_windows = getSlidingWindows(readings)
    return [np.flatten(x) for x in sliding_windows]

def predict(readings)
    flattenedRows = flattenWindows(readings)
    list_of_actions = [classifyMove(flattenedRow) for flattenedRow in flattenedRows]
    return find_consecutive_num(list_of_actions)




