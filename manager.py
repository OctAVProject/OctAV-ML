#!/usr/bin/python3
# coding: utf-8

import os
import config
import sync


def set_working_directory():
    """Set the working directory to the script's directory."""

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


if __name__ == "__main__":
    config.set_logger()
    set_working_directory()
    sync.all()
    sync.git_push()
