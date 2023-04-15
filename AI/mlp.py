import os
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint
from sklearn.feature_selection import SelectKBest, f_classif
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import time 

window_size = 10
slide_by = 1
num_features = 60


moves = ['shield', 'grenade', 'reload', 'logout', 'idle']
index = {label: i for i, label in enumerate(moves)}


def load_har_file(filepath):
    filename = os.path.basename(filepath)
    if any(move in filename for move in moves):
        action = [move for move in moves if move in filename][0]
        print(filename)
        print(action)
    else:
        print(f"No action label found in {filename}")
        return None, None
    label = index[action]

    data = pd.read_csv(filepath, header=None)
    num_windows = int((len(data) - window_size) / slide_by) + 1  
    windows = np.zeros((num_windows, window_size, 6))
    for i in range(0, len(data) - window_size + 1, slide_by):  
        window_data = data.iloc[i:i+window_size, :6].values
        windows[i // slide_by, :, :] = window_data       
    labels = np.full((num_windows,), label)

    return windows, labels

data = {'windows': [], 'labels': []}
for filepath in os.listdir('.'):
    if filepath.endswith('.csv') and any(move in filepath for move in moves):
        windows, labels = load_har_file(filepath)
        if windows is not None and labels is not None:
            data['windows'].append(windows)
            data['labels'].append(labels)
data['windows'] = np.concatenate(data['windows'], axis=0)
data['labels'] = np.concatenate(data['labels'], axis=0)


shuffle_idx = np.random.permutation(len(data['labels']))
data['windows'] = data['windows'][shuffle_idx]
data['labels'] = data['labels'][shuffle_idx]
print(data['windows'])


X = data['windows'].reshape(-1, window_size*6)
print(X)

selector = SelectKBest(f_classif, k=num_features)
selector.fit(X, data['labels'])
X_selected = selector.transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_selected, data['labels'], test_size=0.15, random_state=42)

mlp = MLPClassifier(hidden_layer_sizes=(100, ), max_iter=500, alpha=0.0001,
                    solver='adam', verbose=10, random_state=42)


mlp.fit(X_train, y_train)

score = mlp.score(X_test, y_test)
print("Test set accuracy:", score*100)
