#!/usr/bin/python3
# coding: utf-8

import os
import config
import sync
import model
import argparse
import getpass

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
    group.add_argument("-s", "--sync-only", action="store_true", help="Only perform synchronisation.")
    parser.add_argument("-u", "--vs-user", default=None, help="Username used to connect to VirusShare.")

    args = parser.parse_args()

    if not args.ml_only and args.vs_user is None:
        parser.error("You forgot specify username to perform the connection to VirusShare for synchronization")

    config.set_logger(args.log_level)

    vs_password = getpass.getpass("Password for virusshare.com : ")

    if not args.ml_only and not args.sync_only:
        print("\nSyncing\n")
        sync.all(args.vs_user, vs_password)
        sync.git_push()
        print("Generating model")
        model.create_and_save_model()
    elif args.ml_only:
        print("\nGenerating model\n")
        model.create_and_save_model()
    else:
        print("\nSyncing\n")
        sync.all(args.vs_user, vs_password)
        sync.git_push()

