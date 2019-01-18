# coding: utf-8

"""Thread Safe Configuration Management of OctAV."""

import os
import logging
import threading
from logging.handlers import TimedRotatingFileHandler
import configparser

LOG_DIR = "logs/"
LOG_FILENAME = "octav.log"
CONFIG_FILENAME = "octav.conf"
UPDATER_LOGGER_NAME = "OctAV-Updater"
TENSORFLOW_LOGGER_NAME = "OctAV-TensorFlow"

_updater_logger = logging.getLogger(UPDATER_LOGGER_NAME)
_tensorflow_logger = logging.getLogger(TENSORFLOW_LOGGER_NAME)

_config = configparser.ConfigParser()
_config.read(CONFIG_FILENAME)

# Define _config instance methods as module functions
getstr = _config.get
getint = _config.getint
getfloat = _config.getfloat
getbool = _config.getboolean

_config_lock = threading.Lock()


def set_logger(level=logging.INFO):

    if level is None:
        level = logging.INFO

    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)

    _updater_logger.setLevel(level)
    _updater_logger.propagate = 0
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%m/%d/%Y %H:%M:%S")

    handler = TimedRotatingFileHandler(LOG_DIR + LOG_FILENAME, "W0", backupCount=5)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    _updater_logger.addHandler(handler)

    handler_stdout = logging.StreamHandler()
    handler_stdout.setLevel(level)
    handler_stdout.setFormatter(formatter)
    _updater_logger.addHandler(handler_stdout)

    # TODO : set TensorFlow logger


def update(section, key, value):
    """Update `key` in `section` with the new `value` in `CONFIG_FILENAME`.

    Notes
    -----
    The `value` argument will be converted into a string.
    Every time you update the configuration, it will be written both in memory and in the config file.

    Examples
    --------
        >>> config.update("sync", "last_hashes_file_downloaded", 0)
    """

    with _config_lock:
        _config.set(section, key, str(value))

        with open(CONFIG_FILENAME, "w") as config_file:
            _config.write(config_file)
