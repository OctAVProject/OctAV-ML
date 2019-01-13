#!/usr/bin/python3
# coding: utf-8

<<<<<<< HEAD
"""Updater module for Octav.

    Module used to synchronyze github file repository with public
    lists for malware hashes and malicious domain names et ips.
"""

# LIBRARIES
import requests
import argparse
import datetime
import git

=======
import os
>>>>>>> a5b567d39013f8e7c136548d6cfdaa09e081fe42
import downloader
from git import Repo


<<<<<<< HEAD
# Code
=======
# Set the working directory to the script directory
def set_working_directory():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
>>>>>>> a5b567d39013f8e7c136548d6cfdaa09e081fe42



def retrieve_malicious_domains_and_ips():
<<<<<<< HEAD
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

=======
    downloader.sync_mdl_ips_and_domains()


def retrieve_malware_hashes():
    downloader.sync_md5_hashes()
>>>>>>> a5b567d39013f8e7c136548d6cfdaa09e081fe42


# TODO : use SSH key
def git_push():
<<<<<<< HEAD
    """
        Push new download files to github file repository
    """
    # repo = git.Repo(dl.cm.home_dir)
    # submodule = repo.submodule("files")
    # date = datetime.datetime.now()
    # repo.git.add(".")
    # repo.git.push()
    pass
=======
    repo = Repo("files")

    print("Current commit:", repo.head.commit)
    files_to_add = [item.a_path for item in repo.index.diff(None)] + repo.untracked_files

    if len(files_to_add) > 0:
        repo.git.add(files_to_add)
        print("Added:", files_to_add)
        repo.index.commit("OctAV updated")
        print("New commit:", repo.head.commit)
        repo.remotes.origin.push()
        print("Changes have been pushed to remote repo")

    else:
        print("Push aborted : nothing changed")

>>>>>>> a5b567d39013f8e7c136548d6cfdaa09e081fe42

if __name__ == "__main__":
    """
        Launch updater to synchronize bighub repository.
    """
    print("OctAV updater is starting...")
    set_working_directory()

<<<<<<< HEAD
    dl = downloader.Downloader()

    retrieve_malicious_domains_and_ips()
    # retrieve_malware_hashes()
=======
    #retrieve_malicious_domains_and_ips()
    #retrieve_malware_hashes()
>>>>>>> a5b567d39013f8e7c136548d6cfdaa09e081fe42

    git_push()
