# coding: utf-8

import configparser

CONFIG_FILENAME = "octav.conf"
__config = configparser.ConfigParser()
__config.read(CONFIG_FILENAME)


def get(section, key):

    if section not in __config:
        raise Exception("The section '{}' doesn't exist".format(section))

    if key not in __config[section]:
        raise Exception("The key '{}' doesn't exist in section '{}'".format(section, key))

    return __config[section][key]


def update(section, key, value):

    if section not in __config:
        raise Exception("The section '{}' doesn't exist".format(section))

    __config[section][key] = str(value)

    with open(CONFIG_FILENAME, "w") as config_file:
        __config.write(config_file)
