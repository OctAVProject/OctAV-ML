# coding: utf-8

"""Thread Safe Configuration Management of OctAV."""

import os
import logging
import threading
from logging.handlers import TimedRotatingFileHandler
import configparser

LOG_DIR = "logs/"
UPDATER_LOG_FILENAME = "octav_updater.log"
TENSORFLOW_LOG_FILENAME = "octav_model.log"
REPOFILES_PATH = 'files/'
DATASETS_DIR = REPOFILES_PATH + "datasets/"
MALWARES_DIR = REPOFILES_PATH + "malwares/"
MD5_HASHES_DIR = REPOFILES_PATH + "md5_hashes/"
CONFIG_FILENAME = "octav.conf"
UPDATER_LOGGER_NAME = "OctAV-Updater"
TENSORFLOW_LOGGER_NAME = "OctAV-TensorFlow"
VIRUS_SHARE_BASE_URL = "https://virusshare.com/hashes/VirusShare_"
MDL_URL = "http://www.malwaredomainlist.com/mdlcsv.php"
MD_DOMAIN_URl = "http://www.malware-domains.com/files/justdomains.zip"

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
    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)

    _updater_logger.setLevel(level)
    _updater_logger.propagate = 0
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%m/%d/%Y %H:%M:%S")

    updater_handler = TimedRotatingFileHandler(LOG_DIR + UPDATER_LOG_FILENAME, "W0", backupCount=5)
    updater_handler.setLevel(level)
    updater_handler.setFormatter(formatter)
    _updater_logger.addHandler(updater_handler)

    handler_stdout = logging.StreamHandler()
    handler_stdout.setLevel(level)
    handler_stdout.setFormatter(formatter)
    _updater_logger.addHandler(handler_stdout)

    _tensorflow_logger.setLevel(level)
    _tensorflow_logger.propagate = 0

    model_handler = TimedRotatingFileHandler(LOG_DIR + TENSORFLOW_LOG_FILENAME, "W0", backupCount=5)
    model_handler.setLevel(level)
    model_handler.setFormatter(formatter)
    _tensorflow_logger.addHandler(model_handler)
    _tensorflow_logger.addHandler(handler_stdout)


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
