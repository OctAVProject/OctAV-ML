#!/usr/bin/python3
# coding: utf-8

import os
import downloader
from git import Repo


# Set the working directory to the script directory
def set_working_directory():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


def retrieve_malicious_domains_and_ips():
    downloader.sync_mdl_ips_and_domains()


def retrieve_malware_hashes():
    downloader.sync_md5_hashes()


# TODO : use SSH key
def git_push():
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


if __name__ == "__main__":
    print("OctAV updater is starting...")
    set_working_directory()

    #retrieve_malicious_domains_and_ips()
    #retrieve_malware_hashes()

    git_push()
