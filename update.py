#!/bin/python
# coding: utf-8

"""Updater module for Octav.

    Module used to synchronyze github file repository with public
    lists for malware hashes and malicious domain names et ips.
"""

# LIBRARIES
import requests
import argparse
import datetime
import git

import downloader

# Code

dl = None


def retrieve_malicious_domains_and_ips():
    """
        Download malicious domain names and ips with public lists
        from malwaredomainlist.com
    """
    dl.sync_mdl_ips_and_domains()
    dl.sync_md_domains()


def retrieve_malware_hashes():
    """
        Download malware hashes public lists from malwaredomainlist.com
    """
    dl.sync_md5_hashes()


def git_push():
    """
        Push new download files to github file repository
    """
    # repo = git.Repo(dl.cm.home_dir)
    # submodule = repo.submodule("files")
    # date = datetime.datetime.now()
    # repo.git.add(".")
    # repo.git.push()
    pass

if __name__ == "__main__":
    """
        Launch updater to synchronize bighub repository.
    """
    print("OctAV updater is starting...")

    dl = downloader.Downloader()

    retrieve_malicious_domains_and_ips()
    # retrieve_malware_hashes()

    git_push()
