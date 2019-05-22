# coding: utf-8

from git import Repo, Git
from datetime import datetime

import logging
import requests
import os
import re
import io
import zipfile

import py.config as config
import py.utils as utils

_logger = logging.getLogger(config.UPDATER_LOGGER_NAME)

# TODO : Handle HTTP errors

def all(userVS=None, passwordVS=None):
    _logger.info("Starting to sync everything...")
    _mdl_ips_and_domains()
    _md_domains()
    _md5_hashes()
    if userVS is not None and passwordVS is not None:
        _download_virus_from_virusshare(userVS, passwordVS)


def git_push():
    """Commit new downloaded files to `files` repository and push to remote."""

    git_ssh_identity_file = os.path.expanduser('~/.ssh/git_octav')
    git_ssh_cmd = 'ssh -i {}'.format(git_ssh_identity_file)

    repo = Repo(config.REPOFILES_PATH)

    _logger.debug("Current commit : {}".format(repo.head.commit))
    files_to_add = [item.a_path for item in repo.index.diff(None)] + repo.untracked_files

    if len(files_to_add) == 0:
        _logger.info("Push aborted : nothing changed")
        return

    repo.git.add(files_to_add)
    _logger.debug("Added : {}".format(files_to_add))

    repo.index.commit("OctAV updated")
    _logger.debug("New commit : {}".format(repo.head.commit))

    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        repo.remotes.origin.push()
        _logger.info("Changes have been pushed to remote repo")

    config.update("sync", "last_sync_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def _md5_hashes():
    """Download new hash files from `virusshare.com`."""

    _logger.info("Retrieving MD5 hashes...")

    if not os.path.isdir(config.MD5_HASHES_DIR):
        os.makedirs(config.MD5_HASHES_DIR)

    file_number = config.getint("sync", "last_hashes_file_downloaded")

    while "status code is 200":
        file_number += 1
        url = "{}{:05d}.md5".format(config.VIRUS_SHARE_BASE_URL, file_number)

        _logger.debug("Downloading {}".format(url))
        resp = requests.get(url)
        status = resp.status_code

        # 404 code means we have reached the end of what we need to download
        if status == 404:
            break

        elif status != 200:
            _logger.debug("Unusual error code ({})".format(status))
            raise Exception("Unusual error code ({}).".format(status))

        content = re.sub(r'#.*\n?', '', resp.text, flags=re.MULTILINE)

        with open("{}{:05d}.md5".format(config.MD5_HASHES_DIR, file_number), "w") as hashes_file:
            hashes_file.write(content)

        config.update("sync", "last_hashes_file_downloaded", file_number) 


def _mdl_ips_and_domains():
    """Download new malicious domain names lists from `malwaredomainlist.com`."""

    _logger.info("Retrieving MDL IPs and domain names...")

    if not os.path.isdir(config.REPOFILES_PATH):
        os.makedirs(config.REPOFILES_PATH)

    if not config.getbool("sync", "first_sync_done_from_mdl"):
        _logger.debug("Downloading {}".format(config.MDL_URL))
        resp = requests.get(config.MDL_URL)
        status = resp.status_code

        if status != 200:
            _logger.debug("Error during file download (status {}).".format(status))
            raise Exception("Error during file download (status {}).".format(status))

        with open("{}listIpAndDomains.csv".format(config.REPOFILES_PATH), "w") as list_domains_fp:
            list_domains_fp.write(resp.text)

        utils.sed_in_place(".*?,\"(.*?)\",\"(.*?)\",.*", r"\1,\2", "files/listIpAndDomains.csv")

        config.update("sync", "first_sync_done_from_mdl", True)


def _md_domains():
    """Download new malicious domain name lists from `malware-domains.com`."""

    _logger.info("Retrieving MD domain names...")

    if not os.path.isdir(config.REPOFILES_PATH):
        os.makedirs(config.REPOFILES_PATH)

    _logger.debug("Downloading and extracting {}".format(config.MD_DOMAIN_URl))

    resp = requests.get(config.MD_DOMAIN_URl)
    status = resp.status_code

    if status != 200:
        _logger.debug("Error during file download (status {}).".format(status))
        raise Exception("Error during file download (status {}).".format(resp.status_code))

    zip_file = zipfile.ZipFile(io.BytesIO(resp.content))
    zip_file.extractall(config.REPOFILES_PATH)


def _download_virus_from_virusshare(user, password):
    """Download new malwares from `virusshare.com`."""

    _logger.info("Retrieving malwares...")

    if not os.path.isdir(config.MALWARES_DIR):
        os.makedirs(config.MALWARES_DIR)

    respGetVS = requests.get('https://virusshare.com')
    if respGetVS.status_code == 200:
        cookie = respGetVS.headers['Set-Cookie'].split(";")[0]
        headers = {'Cookie': '{}'.format(cookie)}

        respAuth = requests.post('https://virusshare.com/processlogin.4n6', data = {"username":"{}".format(user), "password":"{}".format(password)}, headers=headers)
        if "NO BOTS! NO SCRAPERS!" not in respAuth.text:
            start = 0
            parser = utils.VirusShareHTMLParser(headers)

            while not parser.stop:
                resp = requests.post('https://virusshare.com/search.4n6', data = {'search':'linux', 'start':'{}'.format(start)}, headers=headers)

                body = resp.text

                parser.feed(body)

                start += 20
        else:
            raise Exception("Error during authentication to VirusShare.")
    else:
        raise Exception("Error, VirusShare is not available (status {}).".format(respGetVS.status_code))
