# coding: utf-8

from argparse import ArgumentParser

from manager import sync
from manager.config import set_logger
from manager.model import data_processing, train_and_save, check_model
from manager.utils import split_dataset, load_dataset_from_csv

if __name__ == "__main__":
    parser = ArgumentParser(prog="python -m manager",
                            description='OctAV Manager : in charge of updating the repository periodically '
                                        'and of performing machine learning.')
    parser.add_argument("-d", "--dataset", required=True,
                        help="The csv dataset")
    parser.add_argument("-l", "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        default="INFO", help="Set the log level")
    parser.add_argument("-t", "--train", action="store_true",
                        help="Train the model and output it as a pickle Python object")
    parser.add_argument("-a", "--assess", action="store_true", help="Assess model.")
    parser.add_argument("-s", "--sync", action="store_true", help="Synchronise the remote git repository")

    args = parser.parse_args()

    set_logger(args.log_level)

    if args.sync:
        sync.all()

    if args.dataset:
        legitimates_syscall, malwares_syscall, max_seq_length = load_dataset_from_csv(args.dataset)
        (X_train, Y_train), (X_check, Y_check), (X_test, Y_test) = split_dataset(legitimates_syscall, malwares_syscall)
        X_train, X_check, X_test = data_processing(X_train, Y_train, X_check, Y_check, X_test, Y_test)

        if args.train:
            train_and_save(X_train, Y_train, max_seq_length)

        if args.assess:
            check_model(X_train, Y_train, X_check, Y_check, X_test, Y_test)

    if args.sync:
        sync.git_push()
