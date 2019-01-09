#!/bin/python
# coding: utf-8

### LIBRARIES
import requests
import argparse
import datetime

import downloader

### Code

dl = None

def retrieve_malicious_domains_and_ips():
    dl.syncMDLIpAndDomain()

def retrieve_malware_hashes():    
    dl.syncMD5Hashes()

def git_push():
    repo = git.Repo(dl.cm.home_dir)
    submodules = repo.submodules
    date = datetime.datetime.now()
    submodules.repo.git.commit("Sync the {} at {}.".format(date.strftime("%d/%m/%Y"), date.strftime("%H:%M:%S")))
    submodules.repo.git.push()

if __name__ == "__main__":
    print("OctAV updater is starting...")

    dl = downloader.Downloader()

    retrieve_malicious_domains_and_ips()
    retrieve_malware_hashes()

    git_push()
