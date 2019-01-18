#!/bin/python
# coding: utf-8

import logging
from logging.handlers import TimedRotatingFileHandler

import configparser

HOME_DIR = "/etc/octav"
LOG_DIR = HOME_DIR + '/logs/'
LOG_FILENAME = 'octav.log'
CONFIG_DIR = HOME_DIR + '/config/'
CONFIG_FILENAME = "octav.conf"

_config = configparser.ConfigParser()
_config.read(CONFIG_DIR + CONFIG_FILENAME)

logger = logging.getLogger("OctavLogger")


def set_logger():
    logger.setLevel(logging.INFO)
    logger.propagate = 0
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%m/%d/%Y %H:%M:%S")

    handler = TimedRotatingFileHandler(LOG_DIR + LOG_FILENAME, "W0", backupCount=5)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler_stdout = logging.StreamHandler()
    handler_stdout.setLevel(logging.INFO)
    handler_stdout.setFormatter(formatter)
    logger.addHandler(handler_stdout)


def get_option(section, key):
    """Get `key` from `section` in `CONFIG_FILENAME`.


    section : str
        Name of the section in which the option is located

    key : str
        Name of the option to get

    Returns
    -------
        str
            Current value for option specified

    Examples
    --------
        >>> config.get_option("last_hashes_file_downloaded")
    """

    if section not in _config:
        logger.exception("Attempt to read a non-existent section '{}'".format(section))
        raise Exception("The section '{}' doesn't exist".format(section))

    if key not in _config[section]:
        logger.exception("Attempt to read a non-existent option '{}' in section '{}'".format(key, section))
        raise Exception("The key '{}' doesn't exist in section '{}'".format(key, section))

    return _config.get(section, key)


def update_option(section, key, value):
    """Update `key` in `section` with the new `value` in `CONFIG_FILENAME`.

    Examples
    --------
        >>> config.update_option("sync", "last_hashes_file_downloaded", 0)
    """

    if section not in _config:
        logger.exception("Attempt to update a non-existent section '{}'".format(section))
        raise Exception("The section '{}' doesn't exist".format(section))

    _config.set(section, key, value)
    logger.info("Updating option '{}' with value '{}' in section '{}'".format(key, value, section))

    with open(CONFIG_DIR + CONFIG_FILENAME, "w") as config_file:
        _config.write(config_file)
