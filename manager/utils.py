# coding: utf-8

from tempfile import mkstemp
from keras.preprocessing.sequence import pad_sequences

import re
import shutil
import logging
import numpy as np
import csv

import manager.config as config
from manager.syscalls import SYSCALLS

_logger_up = logging.getLogger(config.UPDATER_LOGGER_NAME)
_logger_tf = logging.getLogger(config.TENSORFLOW_LOGGER_NAME)


# TODO : load dataset from the sqlite db
def load_dataset(dataset_db):
    pass


# TODO : remove and use DB instead
def load_dataset_from_csv(dataset_path):
    """Read strace files and malwares reports to create a dataset with one-hot-encoded datas."""
    _logger_tf.info("Loading dataset...")

    legits_sys, legits_sys_sequences, legits_label = [], [], [] # seqs = syscall / targs = label
    malwares_sys, malwares_sys_sequences, malwares_label = [], [], []
    legits_max_seq_length, malwares_max_seq_length = 0, 0

    csv.field_size_limit(1000000)

    with open(dataset_path, "r", newline="\n") as dataset_file:
        csv_reader = csv.reader(dataset_file, delimiter=",", quotechar="\"")
        for row in csv_reader:
            syscall_sequences = []
            if row[0] == "0":
                for syscall_sequence in row[1:]:
                    if len(syscall_sequence.split(",")) > 5000:
                        syscall_sequences = []
                        break
                    if syscall_sequence != "":
                        syscall_sequences.append([int(i) for i in syscall_sequence.split(",")])
                if syscall_sequences != []:
                    legits_sys.append(syscall_sequences)
            else:
                for syscall_sequence in row[1:]:
                    if len(syscall_sequence.split(",")) > 5000:
                        syscall_sequences = []
                        break
                    if syscall_sequence != "":
                        syscall_sequences.append([int(i) for i in syscall_sequence.split(",")])
                if syscall_sequences != []:
                    malwares_sys.append(syscall_sequences)        
            
    for sequences_flow in legits_sys:
        sum_seq_size = 0
        for sequence in sequences_flow:
            sum_seq_size += len(sequence)
        if sum_seq_size > legits_max_seq_length:
            legits_max_seq_length = sum_seq_size
    for sequences_flow in malwares_sys:
        sum_seq_size = 0
        for sequence in sequences_flow:
            sum_seq_size += len(sequence)
        if sum_seq_size > legits_max_seq_length:
            malwares_max_seq_length = sum_seq_size
    max_seq_length = max(legits_max_seq_length, malwares_max_seq_length)

    for sequence_flows in legits_sys:
        sys_seq = []
        for syscall_seq in sequence_flows:
            sys_seq += syscall_seq
        legits_sys_sequences.append({"syscall_seq": pad_sequences([sys_seq], maxlen=max_seq_length, padding='post', truncating='post', value=-1)[0]})
                        
    for sequence_flows in malwares_sys:
        sys_seq = []
        for syscall_seq in sequence_flows:
            sys_seq += syscall_seq
        malwares_sys_sequences.append({"syscall_seq": pad_sequences([sys_seq], maxlen=max_seq_length, padding='post', truncating='post', value=-1)[0]})
        
    return legits_sys_sequences, malwares_sys_sequences, max_seq_length


def _cut_dataset_sequences(dataset_sequences, ratios):
    train_split_index = int(round(len(dataset_sequences) * ratios[0]))
    check_split_index = train_split_index + int(round(len(dataset_sequences) * ratios[1]))
    
    #Spread sequences in three parts
    train_sequences = dataset_sequences[:train_split_index]
    check_sequences = dataset_sequences[train_split_index:check_split_index]
    test_sequences = dataset_sequences[check_split_index:]
    
    return train_sequences, check_sequences, test_sequences
    
    
def _shuffle_dataset(legits_sequences, malwares_sequences):
    sequences = np.concatenate((legits_sequences, malwares_sequences))
    labels = np.concatenate(([0] * len(legits_sequences), [1] * len(malwares_sequences)))
    
    indices = np.arange(len(sequences))
    np.random.shuffle(indices)
    
    X = [sequences[i] for i in indices]
    Y = np.array([labels[i] for i in indices])
    
    return X, Y


def split_dataset(legits_sys_sequences, malwares_sys_sequences, ratios=(0.6, 0.2, 0.2)):
    _logger_tf.info("Splittint dataset into train, check and test datasets...")

    #Cut the legits dataset in three parts
    train_legits_sequences, check_legits_sequences, test_legits_sequences = _cut_dataset_sequences(legits_sys_sequences, ratios)
        
    #Cut the malwares dataset in three parts
    train_malwares_sequences, check_malwares_sequences, test_malwares_sequences = _cut_dataset_sequences(malwares_sys_sequences, ratios)
        
    #Shuffle train dataset 
    X_train, Y_train = _shuffle_dataset(train_legits_sequences, train_malwares_sequences)
    
    #Shuffle check dataset
    X_check, Y_check = _shuffle_dataset(check_legits_sequences, check_malwares_sequences)
    
    #Shuffle test dataset
    X_test, Y_test = _shuffle_dataset(test_legits_sequences, test_malwares_sequences)

    return (X_train, Y_train), (X_check, Y_check), (X_test, Y_test)


def sed_in_place(pattern, replace, source):
    """Read file and replace pattern string by replace string"""

    fin = open(source, 'r')

    fd, name = mkstemp()
    fout = open(name, 'w')

    for line in fin:
        out = re.sub(pattern, replace, line)
        fout.write(out)

    fin.close()
    fout.close()

    shutil.move(name, source)


def remove_duplicate_domain_names():
    with open("{}listIpAndDomains.csv".format(config.REPOFILES_PATH), "r") as csvfile:
        mdlcontent = csv.reader(csvfile, delimiter=',', quotechar='"')

    with open("{}justdomains".format(config.REPOFILES_PATH), "r") as mdfile:
        mdcontent = mdfile.read()

    for row in mdlcontent:
        if row[1] in mdcontent:
            sed_in_place(mdlcontent.row[1] + "\n", "", "{}justdomains".format(config.REPOFILES_PATH))
