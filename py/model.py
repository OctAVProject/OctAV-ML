# coding: utf-8

from keras.models import model_from_json
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import GRU
from keras.layers import BatchNormalization
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.preprocessing.sequence import pad_sequences

from contextlib import redirect_stdout

import logging
import datetime
import numpy as np
import argparse
import pickle
import re
import os
import json

import py.config as config
import py.utils as utils

_logger = logging.getLogger(config.TENSORFLOW_LOGGER_NAME)

def _create_model(X_train, Y_train, X_valid, Y_valid):
    """Create and train the neural network model."""

    model = Sequential()
    model.add(Conv1D(filters=32, kernel_size=3, padding='same', activation='tanh', input_shape=(None, config.MAX_SYSCALL_NUM)))
    model.add(BatchNormalization())
    model.add(MaxPooling1D(pool_size=2))
    model.add(GRU(32, dropout=0.2, recurrent_dropout=0.1))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adagrad', metrics=['accuracy'])

    result = model.fit(X_train, Y_train, epochs=10, batch_size=64)

    score, acc = model.evaluate(X_valid, Y_valid, batch_size=64)

    _logger.info("\nTest accuracy : {}".format(acc))
    _logger.info("Test score : {}".format(score))  

    return model


def _classify(predictions, Y_check):
    labels = []

    for index in range(len(Y_check)):
        if predictions[index] > 0.5:
            labels.append(1)
        else:
            labels.append(0)

    return labels


def _build_confusion_table(labels, Y_check):
    #Positive == malware identified
    confusion_table = {"true_positive": 0, "false_positive": 0, "true_negative": 0, "false_negative": 0}
    for index in range(len(labels)):
        if labels[index] == Y_check[index]:
            if labels[index] == 0:
                confusion_table["true_negative"] += 1
            else:
                confusion_table["true_positive"] += 1
        else:
            if labels[index] == 0:
                confusion_table["false_negative"] += 1
            else:
                confusion_table["false_positive"] += 1

    return confusion_table


def _calculate_performance_figures(confusion_table):
    RP = confusion_table["true_positive"] + confusion_table["false_negative"]
    RN = confusion_table["true_negative"] + confusion_table["false_positive"]
    PP = confusion_table["true_positive"] + confusion_table["false_positive"]
    PN = confusion_table["true_negative"] + confusion_table["false_negative"]

    if RP != 0:
        TPR = confusion_table["true_positive"] / RP
    else:
        TPR = confusion_table["true_positive"]
    if RN != 0:
        TNR = confusion_table["true_negative"] / RN
    else:
        TNR = confusion_table["true_negative"]

    if PP != 0:
        PPV = confusion_table["true_positive"] / PP
    else:
        PPV = confusion_table["true_positive"]
    if PN != 0:
        NPV = confusion_table["true_negative"] / PN
    else:
        NPV = confusion_table["true_negative"]

    FPR = 1. - TNR
    FNR = 1. - TPR
    if RP + RN != 0:
        acc = (confusion_table["true_positive"] + confusion_table["true_negative"]) / (RP + RN)
    else:
        acc = confusion_table["true_positive"] + confusion_table["true_negative"]
    if PPV + TPR != 0:
        score = 2 * PPV * TPR / (PPV + TPR)
    else:
        score = 2 * PPV * TPR

    _logger.info("{}\n".format(confusion_table))
    _logger.info("True positive rate : {}".format(TPR))
    _logger.info("True negative rate : {}".format(TNR))
    _logger.info("False positive rate : {}".format(FPR))
    _logger.info("False negative rate : {}".format(FNR))
    _logger.info("Positive predictive value : {}".format(PPV))
    _logger.info("Negative predictive value : {}".format(NPV))
    _logger.info("Accuracy : {}".format(acc))
    _logger.info("Score : {}".format(score))


def create_and_save_model():
    """Create and save the model used by Octav dynamic analysis."""

    if not os.path.isdir(config.REPOFILES_PATH):
        os.makedirs(config.REPOFILES_PATH)

    (X_train, Y_train), (X_valid, Y_valid) = utils.load_train_dataset()

    model = _create_model(X_train, Y_train, X_valid, Y_valid)
    with open("{}octav_model.json".format(config.REPOFILES_PATH), "w") as model_file:
        model_file.write(model.to_json())
    model.save_weights("{}octav_model.hdf5".format(config.REPOFILES_PATH))
    print("Model saved")


def check_model():
    with open("{}octav_model.json".format(config.REPOFILES_PATH), "r") as model_file:
        model_json = model_file.read()
        model = model_from_json(model_json)
    model.load_weights("{}octav_model.hdf5".format(config.REPOFILES_PATH))

    _logger.info("Model loaded")
    model.compile(loss='binary_crossentropy', optimizer='adagrad', metrics=['accuracy'])

    X_check, Y_check = load_check_dataset()

    predictions = model.predict(X_check, batch_size=64, verbose=1)

    labels = _classify(predictions, Y_check)
    confusion_table = _build_confusion_table(labels, Y_check)
    _calculate_performance_figures(confusion_table)