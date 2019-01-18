# coding: utf-8

import logging
import requests
import os
import re
import io
import zipfile
import config
from git import Repo
from datetime import datetime

REPO_PATH = 'files/'
MD5_HASHES_DIR = REPO_PATH + "md5_hashes/"
IP_AND_DOMAINS_DIR = REPO_PATH + "malicious_domains_and_ips/"
VIRUS_SHARE_BASE_URL = "https://virusshare.com/hashes/VirusShare_"
MDL_URL = "http://www.malwaredomainlist.com/mdlcsv.php"
MD_DOMAIN_URl = "http://www.malware-domains.com/files/justdomains.zip"

_logger = logging.getLogger(config.UPDATER_LOGGER_NAME)


# TODO : REMOVE DUPLICATES WITHOUT OVERLOADING THE MEMORY. Bloom filter ?
# TODO : Handle HTTP errors
# TODO : Add SSH key auth to push on GitHub

def all():
    _logger.info("Starting to sync everything...")
    _mdl_ips_and_domains()
    _md_domains()
    _md5_hashes()


def git_push():
    """Commit new downloaded files to `files` repository and push to remote."""

    repo = Repo(REPO_PATH)

    _logger.debug("Current commit : {}".format(repo.head.commit))
    diff = [item.a_path for item in repo.index.diff(None)]
    files_to_add = diff + repo.untracked_files

    if len(files_to_add):

        repo.git.add(files_to_add)
        _logger.debug("Added : {}".format(files_to_add))

        repo.index.commit("OctAV updated")
        _logger.debug("New commit : {}".format(repo.head.commit))

        repo.remotes.origin.push()
        _logger.info("Changes have been pushed to remote repo")

        config.update("sync", "last_sync_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    else:
        _logger.info("Push aborted : nothing changed")


def _md5_hashes():
    """Download new hash files from `virusshare.com`."""

    _logger.info("Retrieving MD5 hashes...")

    if not os.path.isdir(MD5_HASHES_DIR):
        os.makedirs(MD5_HASHES_DIR)

    file_number = config.getint("sync", "last_hashes_file_downloaded") + 1
    status = 200

    while status == 200:
        file_number_s = str(file_number).zfill(5)
        url = VIRUS_SHARE_BASE_URL + file_number_s + ".md5"
        _logger.debug("Downloading {}".format(url))
        resp = requests.get(url)
        status = resp.status_code
        body = resp.text
        body = re.sub(r'#.*\n?', '', body, flags=re.MULTILINE)

        if status == 200:
            with open("{}{}.md5".format(MD5_HASHES_DIR, file_number_s), "w") as hashes_fp:
                hashes_fp.write(body)
            file_number += 1

    # code 404 means we have reached the end of what we need to download
    if status != 404:
        raise Exception("Unusual error code ({}).".format(status))

    config.update("sync", "last_hashes_file_downloaded", file_number - 1)


def _mdl_ips_and_domains():
    """Download new malicious domain names lists from `malwaredomainlist.com`."""

    _logger.info("Retrieving MDL IPs and domain names...")

    if not os.path.isdir(IP_AND_DOMAINS_DIR):
        os.makedirs(IP_AND_DOMAINS_DIR)

    if config.getbool("sync", "first_sync_done_from_mdl"):
        _logger.info("Downloading {}".format(MDL_URL))
        resp = requests.get(MDL_URL)
        status = resp.status_code
        body = resp.text
        if status == 200:
            with open("{}listIpAndDomains.csv".format(IP_AND_DOMAINS_DIR), "a") as list_domains_fp:
                list_domains_fp.write(body)
            config.update("sync", "first_sync_done_from_mdl", True)
        else:
            raise Exception("Error during file download (status {}).".format(status))


def _md_domains():
    """Download new malicious domain name lists from `malware-domains.com`."""

    _logger.info("Retrieving MD domain names...")

    if not os.path.isdir(IP_AND_DOMAINS_DIR):
        os.makedirs(IP_AND_DOMAINS_DIR)

    _logger.debug("Downloading and extracting {}".format(MD_DOMAIN_URl))
    resp = requests.get(MD_DOMAIN_URl)
    zip_file = zipfile.ZipFile(io.BytesIO(resp.content))
    status = resp.status_code
    if status == 200:
        zip_file.extractall("{}".format(IP_AND_DOMAINS_DIR))
    else:
        raise Exception("Error during file download (status {}).".format(resp.status_code))
