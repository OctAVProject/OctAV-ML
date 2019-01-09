#!/bin/python

"""Configuration management for Octav.

Configuration file is located in the <homedir>/config directory. This file contains tools to
manage these configuration files.
"""

### LIBRARIES

import configparser
import fcntl
import logging
import os
import os.path
import sys
import argparse

### Check the home directory and configuration directory for the application

HOME_DIR = os.getenv("OCTAV_HOME")

if not HOME_DIR:
    print("Need to setup OCTAV_HOME environment variable, see readme")
    sys.exit()

CONFIG_DIR = HOME_DIR + '/config'
LOG_DIR = HOME_DIR + '/logs'

### Code

class ConfigurationManager(object):
    """Configuration management for Octav.

    Configuration files is located in the <homedir>/config directory. This file contains tools
    to manage these configuration files.
    """

    def __init__(self, param_config=None):
        # path and file locations
        self.home_dir = os.getenv("OCTAV_HOME")
        self.config_dir = self.home_dir + "/config/"
        self.log_dir = self.home_dir + "/logs/"
        self.files_dir = self.home_dir + "/files/"

        self.param_config = param_config

        # Configparsers
        self.config = configparser.RawConfigParser(allow_no_value=True)
        self.loadConfig()  

        self.sync = None
        self.setSync()

    def loadConfig(self):
        """Load config files into configparser instance"""
        with open(self.config_dir + 'config.cfg') as configFp:
            fcntl.lockf(configFp, fcntl.LOCK_SH)
            self.config.readfp(configFp, self.config_dir + 'config.cfg')
            fcntl.lockf(configFp, fcntl.LOCK_UN)

    def updateConfig(self, name, value, configSection):
        """Update the application state (name / value pair)

        :param name: option name to update
        :type name: str

        :param value: value to update option name to
        :type value: str
        """
        value = str(value)
        logging.info('Updating application config {%s: %s}', name, value)

        if not self.config.has_section(configSection):
            print("Section {} not found in config file".format(configSection))
            sys.exit()

        self.config.set(configSection, name, value)

        with open(self.config_dir + 'config.cfg', 'w') as configFp:
            fcntl.lockf(configFp, fcntl.LOCK_EX)
            self.config.write(configFp)
            fcntl.lockf(configFp, fcntl.LOCK_UN)

    def setSync(self):

        sync = dict()

        sync["lastHashesFileDownloaded"] = self.config.get('sync', 'lastHashesFileDownloaded')
            
        self.sync = Section(sync)


class Section(object):
    def __init__(self, config):
        self.config = config
        self.setValues(self.config)

    def setConfig(self, config):
        self.config = config
        self.setValues(self.config)

    def getConfig(self):
        return self.config

    def setValue(self, key, value):
        setattr(self, key, value)

    def setValues(self, dict_of_items):
        """Create class instance variables from key, value pairs

        :param dict_of_items: a dict containing key, value pairs to set
        :type dict_of_items: dict
        """
        for key, value in dict_of_items.items():
            setattr(self, key, value)

    def get(self, item):
        """Get class instance variables from string

        :param item:
        :type item: str

        :return: object of item type
        :rtype: object
        """
        return getattr(self, item)


if __name__ == "__main__":
    # prints the current configuration

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default=None, help='Config File Override')
    args = parser.parse_args()

    cm = ConfigurationManager(param_config=args.config)

    if args.config:
        print("Configuration File : {}\n".format(args.config))
    elif os.path.isfile(CONFIG_DIR + '/overrides.cfg'):
        print("Configuration File: overrides.cfg\n")
    else:
        print("Configuration File: config.cfg\n")

    print("Home directory set : {}".format(HOME_DIR))
    print("Config directory set : {}".format(CONFIG_DIR))
    print("Logs directory set : {}".format(LOG_DIR))

    print("\n#Sync Configuration")
    for h_key, h_value in cm.sync.config.items():
        print(h_key, "=", h_value)