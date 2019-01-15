#!/bin/python
# coding: utf-8

"""Configuration management for Octav updater.

    Configuration file is located in the <homedir>/config directory.
    This file contains tools to manage these configuration files.
"""
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

logger = logging.getLogger("Octav Log")


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
    """
        Get class instance variables from name.

        :param section: Name of the section in which the option is located
        :type section: str
        :param key: Name of the option to get
        :type key: str
        :return: current value for option specified
        :rtype: str

        :Example:
        >>> config.get_option("last_hashes_file_downloaded")
    """
    if section not in _config:
        logger.exception('Attempt to read a non-existent section ({})'.format(section))
        raise Exception("The section '{}' doesn't exist".format(section))

    if key not in _config[section]:
        logger.exception('Attempt to read a non-existent option in section {} ({})'.format(section, key))
        raise Exception("The key '{}' doesn't exist in section '{}'".format(section, key))

    return _config.get(section, key)


def update_option(section, key, value):
    """
        Update the application configuration (name / value pair).
        Excluside lock is used to block shared lock (read mode).

        :param section: section name in which is located the option
        :type section: str
        :param key: option name to update
        :type key: str
        :param value: new value to save
        :type value: str

        :Example:
        >>> config.update_option("sync", "last_hashes_file_downloaded", "0")
    """
    if section not in _config:
        logger.exception('Attempt to update a non-existent option in section {} ({}: {})'.format(section, key, value))
        raise Exception("The section '{}' doesn't exist".format(section))

    _config.set(section, key, value)
    logger.info('Updating application config ({}: {}) in section {}'.format(key, value, section))

    with open(CONFIG_DIR + CONFIG_FILENAME, "w") as config_file:
        _config.write(config_file)
