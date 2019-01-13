#!/bin/python
# coding: utf-8

"""Configuration management for Octav updater.

    Configuration file is located in the <homedir>/config directory.
    This file contains tools to manage these configuration files.
"""

# LIBRARIES
import os
import os.path
import sys
import fcntl
import logging

import configparser

# Check the home directory and configuration directory for the application

HOME_DIR = "/etc/octav"
CONFIG_DIR = HOME_DIR + '/config/'
LOG_DIR = HOME_DIR + '/logs/'


# Code

class ConfigurationManager(object):
    """Configuration management for Octav.

        Configuration files is located in the <CONFIG_DIR> directory.
        This file contains tools to manage these configuration files.
    """

    def __init__(self):
        """
            Initialize the configuration of Octav parsing the config
            file stored in /etc/octav/config.
        """
        self._config = configparser.RawConfigParser(allow_no_value=True)
        self._load_config()

        self.sync = None
        self._set_sync()

    def _load_config(self):
        """
            Load config files into configparser instance. Shared lock block
            reading if file is locked with exclusive lock (write mode).
        """
        with open(CONFIG_DIR + 'config.cfg') as config_fp:
            fcntl.lockf(config_fp, fcntl.LOCK_SH)
            self._config.readfp(config_fp, CONFIG_DIR + 'config.cfg')
            fcntl.lockf(config_fp, fcntl.LOCK_UN)

    def _set_sync(self):
        """
            Create an instance of Section to store the options of sync
            section in the config file.
        """
        sync = dict()
        section_name = "sync"

        option_name = "last_hashes_file_downloaded"
        sync[option_name] = self._config.get(section_name, option_name)
        option_name = "first_sync_done_from_mdl"
        sync[option_name] = self._config.get(section_name, option_name)
        self.sync = Section(sync)

    def update_config(self, name, value, config_section):
        """
            Update the application configuration (name / value pair).
            Excluside lock is used to block shared lock (read mode).

            :param name: option name to update
            :type name: str
            :param value: new value to save
            :type value: str
            :param config_section: section name in which is located the option
            :type config_section: str

            :Example:
            >>> cm.update_config("last_hashes_file_downloaded", "0", "sync")

            .. todo:: Update value in Section instance too

        """
        value = str(value)
        logging.info('Updating application config {%s: %s}', name, value)

        if not self._config.has_section(config_section):
            print("Section {} not found in config file".format(config_section))
            sys.exit()

        self._config.set(config_section, name, value)
        self.sync.set_config(self._config)

        with open(CONFIG_DIR + 'config.cfg', 'w') as config_fp:
            fcntl.lockf(config_fp, fcntl.LOCK_EX)
            self._config.write(config_fp)
            fcntl.lockf(config_fp, fcntl.LOCK_UN)


class Section(object):
    """Storage objects for configuration parameters.

        Store each option defined in the config file in attributes.
    """

    def __init__(self, config):
        """
            Initialize the Section object with values read in config file.

            :param config: a dict containing key/value pairs to set
            :type config: dict

            :Example:
            >>> Section({"last_hashes_file_downloaded": -1})
        """
        self._config = config
        self._set_values(self._config)

    def set_config(self, config):
        """
            Set new values for all options.

            :param config: a dict containing key/value pairs to update
            :type config: dict

            :Example:
            >>> section.set_config({"last_hashes_file_downloaded": 0})
        """
        self._config = config
        self._set_values(self._config)

    def get_config(self):
        """
            Get the dict containing all key/value pairs.

            :return: a dict containing all key/value pairs
            :rtype: dict

            :Example:
            >>> section.get_config()
        """
        return self._config

    def _set_value(self, key, value):
        """
            Set attribute value identified by name.

            :param key: option name
            :type key: str
            :param value: new value for option
            :type value: str

            :Example:
            >>> self.__set_value("last_hashes_file_downloaded", "1")
        """
        setattr(self, key, value)

    def _set_values(self, dict_of_items):
        """
            Set all attribute values stored in dict_of_items for this instance.

            :param dict_of_items: a dict containing key/value pairs to update
            :type dict_of_items: dict

            :Example:
            >>> self.__set_values({"last_hashes_file_downloaded", "1"})
        """
        for key, value in dict_of_items.items():
            self._set_value(key, value)

    def get(self, item):
        """
            Get class instance variables from name.

            :param item: Name of the option to get
            :type item: str
            :return: current value for option specified
            :rtype: str

            :Example:
            >>> get("last_hashes_file_downloaded")
        """
        return getattr(self, item)


if __name__ == "__main__":
    """
        Print Octav configuration.
    """
    cm = ConfigurationManager()

    print("Home directory set : {}".format(HOME_DIR))
    print("Config directory set : {}".format(CONFIG_DIR))
    print("Logs directory set : {}".format(LOG_DIR))

    print("\n#Sync Configuration")
    for key in cm.sync.get_config().keys():
        print(key, "=", cm.sync.get(key))
