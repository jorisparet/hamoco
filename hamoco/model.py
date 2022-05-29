#TODO: remove sklearn dependence

import os

import numpy
import keras
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .hand import Hand

class ClassificationModel:

    # TODO: read automatically from mediapipe.solutions.hands
    n_features = 42

    def __init__(self):
        self.num_classes = len(Hand.Pose)
        self.model = Sequential()

    def read_sample(self, path_to_sample):
        with open(path_to_sample, 'r') as file:
            # label
            y_i = int(file.readline())
            # features
            x_i = file.readline().split()
            x_i = list(map(numpy.float32, x_i))
            return x_i, y_i

    def read_dataset(self, path_to_dataset):
        # list of sample files
        paths_to_dataset_files = os.listdir(path_to_dataset)
        paths_to_dataset_files = [os.path.join(path_to_dataset, f) for f in paths_to_dataset_files if f.endswith('.dat')]
        paths_to_dataset_files.sort()
        n_samples = len(paths_to_dataset_files)

        # Fill the dataset
        X = numpy.empty((n_samples, self.n_features), dtype=numpy.float32)
        y = numpy.empty(n_samples, dtype=numpy.int32)
        for i, sample in enumerate(paths_to_dataset_files):
            x_i, y_i = self.read_sample(sample)
            X[i,:] = x_i
            y[i] = y_i
        self.data = X
        self.classes = y
        self.n_samples = n_samples

    def process_dataset(self):
        # Translate points back based on the center of mass of the hand
        for i in range(self.n_samples):
            self.data[i,0::2] -= self.data[i,0::2].mean() # x
            self.data[i,1::2] -= self.data[i,1::2].mean() # y

    def train(self, hidden_layers=(50,25,10), learning_rate=0.01, epochs=15, test_size=0.30):
        # Model
        for layer, size in enumerate(hidden_layers):
            # first hidden layer
            if layer == 0:
                self.model.add(Dense(size, activation='relu', 
                                input_shape=(self.n_features,)))
            # intermediate hidden layers
            elif layer < len(hidden_layers) - 1:
               self.model.add(Dense(size, activation='relu')) 
            # last hidden layer (prediction with softmax)
            else:
                self.model.add(Dense(self.num_classes, activation='softmax'))

        # Optimizer
        optimizer = keras.optimizers.adam_v2.Adam(learning_rate=learning_rate)
        self.model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        # Train
        X_train, X_test, y_train, y_test = train_test_split(self.data, self.classes, test_size=test_size)
        _ = self.model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=epochs, verbose=2)

    def save_model(self, path):
        self.model.save(path)