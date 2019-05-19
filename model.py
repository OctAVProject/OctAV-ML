# coding: utf-8

from keras.datasets import imdb
from keras.models import model_from_json
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import GRU
from keras.layers import Dropout
from keras.layers import BatchNormalization
from keras.layers import Flatten
from keras.callbacks import History
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.preprocessing.sequence import pad_sequences

from contextlib import redirect_stdout

import datetime
import numpy as np
import argparse
import pickle
import re
import os
import json

from syscalls import SYSCALLS
    
MAX_SYSCALL_NUM=32
VALIDATION=0.2

def _load_dataset():
    """Read strace files and malwares reports to create a dataset with one-hot-encoded datas."""
    seqs, targs = [], []

    for subdir, dirs, files in os.walk("data/dataset_legits"):
        for file in files:
            if file.endswith(".strace"):

                filepath = os.path.join(subdir, file)
                print("Loading ", filepath)



                syscall_seq = []

                with open(filepath, "r") as f:
                    content = f.read()
                    for m in re.finditer(r"([a-z_0-9]+)\(", content):
                        syscall = m.group(1)
                        if syscall in SYSCALLS:
                            syscall_num = SYSCALLS[syscall]
                            if syscall_num < MAX_SYSCALL_NUM:
                                syscall_seq.append(syscall_num)

                one_hot_encoded = np.eye(MAX_SYSCALL_NUM)[syscall_seq]

                seq = np.concatenate((one_hot_encoded, np.zeros((1,MAX_SYSCALL_NUM))))
                seq_len = seq.shape[0]

                seqs.append(seq)
                targs.append(0)

    for subdir, dirs, files in os.walk("data/dataset_malwares"):
        for file in files:
            if file.endswith(".json"):

                filepath = os.path.join(subdir, file)
                print("Loading ", filepath)



                syscall_seq = []

                with open(filepath, "r") as f:
                    content = f.read()
                    for m in re.finditer(r"\.*?api.: .([a-z_0-9]+)", content):
                        syscall = m.group(1)
                        if syscall in SYSCALLS:
                            syscall_num = SYSCALLS[syscall]
                            if syscall_num < MAX_SYSCALL_NUM:
                                syscall_seq.append(syscall_num)

                one_hot_encoded = np.eye(MAX_SYSCALL_NUM)[syscall_seq]

                seq = np.concatenate((one_hot_encoded, np.zeros((1,MAX_SYSCALL_NUM))))
                seq_len = seq.shape[0]

                seqs.append(seq)
                targs.append(1)


    indices = np.arange(len(seqs))
    np.random.shuffle(indices)

    split_index = int(len(seqs) * VALIDATION)

    train_indices = indices[split_index:]
    valid_indices = indices[:split_index]

    X_train = [seqs[i] for i in train_indices]
    X_valid = [seqs[i] for i in valid_indices]

    Y_train = np.array([targs[i] for i in train_indices])
    Y_valid = np.array([targs[i] for i in valid_indices])

    X_train = pad_sequences(X_train)
    X_valid = pad_sequences(X_valid)

    return (X_train, Y_train) , (X_valid, Y_valid)


def _create_model(X_train, Y_train, X_valid, Y_valid):
    """Create and train the neural network model."""

    model = Sequential()
    model.add(Conv1D(filters=32, kernel_size=3, padding='same', activation='tanh', input_shape=(None, MAX_SYSCALL_NUM)))
    model.add(BatchNormalization())
    model.add(MaxPooling1D(pool_size=2))
    model.add(GRU(32, dropout=0.2, recurrent_dropout=0.1))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adagrad', metrics=['accuracy'])

    result = model.fit(X_train, Y_train, epochs=10, batch_size=64)

    score, acc = model.evaluate(X_valid, Y_valid, batch_size=64)

    print('Test score:', score)
    print('Test accuracy:', acc)    

    return model


def create_and_save_model():
    """Create and save the model used by Octav dynamic analysis."""

    (X_train, Y_train), (X_valid, Y_valid) = _load_dataset()

    model = _create_model(X_train, Y_train, X_valid, Y_valid)
    with open("files/octav_model.json", "w") as model_file:
        model_file.write(model.to_json())
    model.save_weights("files/octav_model.hdf5")
    print("Model saved")