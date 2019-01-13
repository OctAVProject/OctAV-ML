#!/usr/bin/python3
# coding: utf-8

"""Updater module for Octav.

    Module used to synchronyze github file repository with public
    lists for malware hashes and malicious domain names et ips.
"""

# LIBRARIES
import requests
import argparse
import datetime
import os

from git import Repo

import downloader


# Code

# Set the working directory to the script directory
def set_working_directory():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


def retrieve_malicious_domains_and_ips():
    """
        Download malicious domain names and ips with public lists
        from malwaredomainlist.com
    """
    downloader.sync_mdl_ips_and_domains()
    downloader.sync_md_domains()


def retrieve_malware_hashes():
    """
        Download malware hashes public lists from malwaredomainlist.com
    """
    downloader.sync_md5_hashes()


# TODO : use SSH key
def git_push():
    """
        Push new download files to github file repository
    """
    repo = Repo("files")

    print("Current commit:", repo.head.commit)
    files_to_add = [item.a_path for item in repo.index.diff(None)]
    + repo.untracked_files

    if len(files_to_add) > 0:
        repo.git.add(files_to_add)
        print("Added:", files_to_add)
        repo.index.commit("OctAV updated")
        print("New commit:", repo.head.commit)
        repo.remotes.origin.push()
        print("Changes have been pushed to remote repo")

    else:
        print("Push aborted : nothing changed")


if __name__ == "__main__":
    """
        Launch updater to synchronize bighub repository.
    """
    print("OctAV updater is starting...")
    set_working_directory()
    retrieve_malicious_domains_and_ips()
    retrieve_malware_hashes()
    git_push()
