#!/usr/bin/python3
# coding: utf-8

import os
import config
import sync
import argparse


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

    parser.add_argument("--ml-only", action="store_true", help="Only perform machine learning.")
    parser.add_argument("--sync-only", action="store_true", help="Only perform synchronisation.")

    args = parser.parse_args()

    if args.ml_only and args.sync_only:
        parser.error("You cannot specify both ml-only and sync-only at the same time")

    config.set_logger(args.log_level)

    sync.all()
    sync.git_push()
