#!/usr/bin/python3
# coding: utf-8

import datetime
import os
from git import Repo
import logging
import config
import downloader

_logger = logging.getLogger(config.UPDATER_LOGGER_NAME)


def set_working_directory():
    """Set the working directory to the script's directory."""

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


def retrieve_malicious_domains_and_ips():
    downloader.sync_mdl_ips_and_domains()
    downloader.sync_md_domains()


def retrieve_malware_hashes():
    downloader.sync_md5_hashes()


# TODO : use SSH key
def git_push():
    """Commit new downloaded files to `files` repository and push to remote."""

    repo = Repo("/etc/octav/files")

    _logger.info("Current commit : {}".format(repo.head.commit))
    diff = [item.a_path for item in repo.index.diff(None)]
    files_to_add = diff + repo.untracked_files

    if len(files_to_add):
        repo.git.add(files_to_add)
        _logger.info("Added : {}".format(files_to_add))
        repo.index.commit("OctAV updated")
        _logger.info("New commit : {}".format(repo.head.commit))
        repo.remotes.origin.push()
        _logger.info("Changes have been pushed to remote repo")

        date = datetime.datetime.now()
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        config.update("sync", "last_sync_date", date)
    else:
        _logger.info("Push aborted : nothing changed")


if __name__ == "__main__":
    config.set_logger()
    _logger.info("OctAV updater is starting...")
    set_working_directory()

    retrieve_malicious_domains_and_ips()
    retrieve_malware_hashes()
    git_push()
