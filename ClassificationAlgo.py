import numpy
def classifyMove(flattenedData)
    overlay = Overlay('design_1_wrapper.bit')
    dma = overlay.axi_dma_0

    input_buffer = allocate(shape=(180,), dtype=np.float32)
    output_buffer = allocate(shape=(1,), dtype=np.float32)

    inputData=flattenedData

    for x, n in enumerate(inputData):
        input_buffer[x] = n
    dma.sendchannel.transfer(input_buffer)
    dma.recvchannel.transfer(output_buffer)
    dma.sendchannel.wait()
    dma.recvchannel.wait()

    return action 

def getSlidingWindows(readings, window_size, 1):
    result = []
    for i in range(0, len(readings) - window_size + 1, 1):
        result.append(readings[i:i + window_size])
    return result
    
def  flattenTheWindows():
    sliding_windows = MyClass.getSlidingWindows(data, window_size, 1)
    return [np.flatten(x) for x in sliding_windows]
