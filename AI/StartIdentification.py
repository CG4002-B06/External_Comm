import pandas as pd
import numpy as np


def calculate_threshold(window_data):
    acc_values = window_data[:, :3]
    acc_range = np.max(acc_values, axis=0) - np.min(acc_values, axis=0)
    return np.sum(acc_range) / len(acc_range)

def detect_move(data, window_size, slide_val):
    start_of_move_flag = False
    num_windows = int((len(data) - window_size) / slide_val) + 1  
    windows = np.zeros((num_windows, window_size, 6))
    for i in range(0, len(data) - window_size + 1, slide_val):
        window_data = data.iloc[i:i+window_size, :6].values
        windows[i // slide_val, :, :] = window_data
        threshold = calculate_threshold(window_data)
        if threshold > 500:
            start_of_move_flag = True
    return start_of_move_flag

window_size = 3
slide_size = 2
# start_of_move_flag = detect_move(data, window_size, slide_size)
