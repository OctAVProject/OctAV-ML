#!/usr/bin/python3
# coding: utf-8

import os
import argparse
import getpass
import numpy
import logging
import pickle

import model.config as config
import model.sync as sync
import model.model as model
import model.utils as utils

def set_working_directory():
    """Set the working directory to the script's directory."""

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


if __name__ == "__main__":
    set_working_directory()

    parser = argparse.ArgumentParser(description='OctAV Manager : in charge of updating the repository periodically '
                                                 'and of performing machine learning.')
    parser.add_argument("-l", "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        default="INFO", help="Set the log level")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-m", "--ml-only", action="store_true", help="Only perform machine learning.")
    group.add_argument("-c", "--check_model", action="store_true", help="Only assess model.")
    group.add_argument("-s", "--sync-only", action="store_true", help="Only perform synchronisation.")

    args = parser.parse_args()

    config.set_logger(args.log_level)

    if not args.ml_only and not args.sync_only and not args.check_model:
        sync.all()

        DATASET_PATH = "dataset.csv"
        legitimates_syscall, malwares_syscall, max_seq_length = utils.generate_dataset(DATASET_PATH)
        (X_train, Y_train) , (X_check, Y_check), (X_test, Y_test) = utils.split_dataset(legitimates_syscall, malwares_syscall)
        
        X_train, X_check, X_test = model.data_processing(X_train, Y_train, X_check, Y_check, X_test, Y_test)
        
        octav_model = model.create_and_save_model(X_train, Y_train, max_seq_length)

        model.check_model(X_train, Y_train, X_check, Y_check, X_test, Y_test, octav_model)

        sync.git_push()
    elif args.ml_only:
        
        DATASET_PATH = "dataset.csv"
        legitimates_syscall, malwares_syscall, max_seq_length = utils.generate_dataset(DATASET_PATH)
        (X_train, Y_train) , (X_check, Y_check), (X_test, Y_test) = utils.split_dataset(legitimates_syscall, malwares_syscall)
        
        X_train, X_check, X_test = model.data_processing(X_train, Y_train, X_check, Y_check, X_test, Y_test)
        
        octav_model = model.create_and_save_model(X_train, Y_train, max_seq_length)

        model.check_model(X_train, Y_train, X_check, Y_check, X_test, Y_test, octav_model)
    elif args.check_model:
        
        DATASET_PATH = "dataset.csv"
        legitimates_syscall, malwares_syscall, max_seq_length = utils.generate_dataset(DATASET_PATH)
        (X_train, Y_train) , (X_check, Y_check), (X_test, Y_test) = utils.split_dataset(legitimates_syscall, malwares_syscall)
        
        X_train, X_check, X_test = model.data_processing(X_train, Y_train, X_check, Y_check, X_test, Y_test)
        
        model_file_path = "files/"
        for filename in os.listdir(model_file_path):
            if filename.startswith('random_forest_model'):
                model_file_path += filename
        
        octav_model = pickle.load(open(model_file_path, 'rb'))

        model.check_model(X_train, Y_train, X_check, Y_check, X_test, Y_test, octav_model)
    else:
        sync.all()
        sync.git_push()

