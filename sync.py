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
from html.parser import HTMLParser

REPO_PATH = 'files/'
MD5_HASHES_DIR = REPO_PATH + "md5_hashes/"
IP_AND_DOMAINS_DIR = REPO_PATH + "malicious_domains_and_ips/"
MALWARES_DIR = REPO_PATH + "malwares/"
VIRUS_SHARE_BASE_URL = "https://virusshare.com/hashes/VirusShare_"
MDL_URL = "http://www.malwaredomainlist.com/mdlcsv.php"
MD_DOMAIN_URl = "http://www.malware-domains.com/files/justdomains.zip"

_logger = logging.getLogger(config.UPDATER_LOGGER_NAME)


# TODO : REMOVE DUPLICATES WITHOUT OVERLOADING THE MEMORY. Bloom filter ?
# TODO : Handle HTTP errors
# TODO : Add SSH key auth to push on GitHub

def all(userVS=None, passwordVS=None):
    _logger.info("Starting to sync everything...")
    _mdl_ips_and_domains()
    _md_domains()
    _md5_hashes()
    if userVS is not None and passwordVS is not None:
        _download_virus_from_virusshare(userVS, passwordVS)


def git_push():
    """Commit new downloaded files to `files` repository and push to remote."""

    repo = Repo(REPO_PATH)

    _logger.debug("Current commit : {}".format(repo.head.commit))
    files_to_add = [item.a_path for item in repo.index.diff(None)] + repo.untracked_files

    if len(files_to_add) == 0:
        _logger.info("Push aborted : nothing changed")
        return

    repo.git.add(files_to_add)
    _logger.debug("Added : {}".format(files_to_add))

    repo.index.commit("OctAV updated")
    _logger.debug("New commit : {}".format(repo.head.commit))

    repo.remotes.origin.push()
    _logger.info("Changes have been pushed to remote repo")

    config.update("sync", "last_sync_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def _md5_hashes():
    """Download new hash files from `virusshare.com`."""

    _logger.info("Retrieving MD5 hashes...")

    if not os.path.isdir(MD5_HASHES_DIR):
        os.makedirs(MD5_HASHES_DIR)

    file_number = config.getint("sync", "last_hashes_file_downloaded")

    while "status code is 200":
        file_number += 1
        url = "{}{:05d}.md5".format(VIRUS_SHARE_BASE_URL, file_number)

        _logger.debug("Downloading {}".format(url))
        resp = requests.get(url)

        # 404 code means we have reached the end of what we need to download
        if resp.status_code == 404:
            break

        elif resp.status_code != 200:
            raise Exception("Unusual error code ({}).".format(resp.status_code))

        content = re.sub(r'#.*\n?', '', resp.text, flags=re.MULTILINE)

        with open("{}{:05d}.md5".format(MD5_HASHES_DIR, file_number), "w") as hashes_file:
            hashes_file.write(content)

        config.update("sync", "last_hashes_file_downloaded", file_number)


def _mdl_ips_and_domains():
    """Download new malicious domain names lists from `malwaredomainlist.com`."""

    _logger.info("Retrieving MDL IPs and domain names...")

    if not os.path.isdir(IP_AND_DOMAINS_DIR):
        os.makedirs(IP_AND_DOMAINS_DIR)

    if config.getbool("sync", "first_sync_done_from_mdl"):
        _logger.debug("Downloading {}".format(MDL_URL))
        resp = requests.get(MDL_URL)
        status = resp.status_code

        if status != 200:
            raise Exception("Error during file download (status {}).".format(status))

        with open("{}listIpAndDomains.csv".format(IP_AND_DOMAINS_DIR), "a") as list_domains_fp:
            list_domains_fp.write(resp.text)

        config.update("sync", "first_sync_done_from_mdl", True)


def _md_domains():
    """Download new malicious domain name lists from `malware-domains.com`."""

    _logger.info("Retrieving MD domain names...")

    if not os.path.isdir(IP_AND_DOMAINS_DIR):
        os.makedirs(IP_AND_DOMAINS_DIR)

    _logger.debug("Downloading and extracting {}".format(MD_DOMAIN_URl))

    resp = requests.get(MD_DOMAIN_URl)

    if resp.status_code != 200:
        raise Exception("Error during file download (status {}).".format(resp.status_code))

    zip_file = zipfile.ZipFile(io.BytesIO(resp.content))
    zip_file.extractall(IP_AND_DOMAINS_DIR)


class VirusShareHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.in_table = False
        self.in_a = False
        self.date_in_next = False
        self.out_of_a = False
        self.dl_url = ""
        self.stop = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        elif tag == "a" and self.in_table and not self.dl_url:
            enf_of_url = attrs[0][1]
            self.dl_url = "https://virusshare.com/{}".format(enf_of_url)
        elif tag == "a" and self.in_table:
            self.date_in_next = True
            

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False

    def handle_data(self, data):
        if self.date_in_next and not self.out_of_a:
            self.out_of_a = True
        elif self.date_in_next and self.out_of_a:
            date = data.split("submitted ")[1]
            date = date.split(" UTC")[0]
            print(date)
            date_t = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            date_base = datetime.datetime.strptime("2016-07-15 23:27:31", "%Y-%m-%d %H:%M:%S")
            if date_base < date_t:
                print(self.dl_url)

                print("Downloading...")
                resp = requests.get(self.dl_url, headers=headers)
                zip_file = zipfile.ZipFile(io.BytesIO(resp.content))
                status = resp.status_code
                if status == 200:
                    zip_file.extractall(MALWARES_DIR, pwd=str.encode("infected"))
                else:
                    raise Exception("Error during file downloading (status {}).".format(resp.status_code))
            else:
                print("Stopping...")
                self.stop = True

            self.out_of_a = False
            self.dl_url = ""
            self.date_in_next = False


def _download_virus_from_virusshare(user, password):
    """Download new malwares from `virusshare.com`."""

    _logger.info("Retrieving malwares...")

    if not os.path.isdir(MALWARES_DIR):
        os.makedirs(MALWARES_DIR)

    respGetVS = requests.get('https://virusshare.com')
    if respGetVS.status_code == 200:
        cookie = respGetVS.headers['Set-Cookie'].split(";")[0]
        headers = {'Cookie': '{}'.format(cookie)}

        respAuth = requests.post('https://virusshare.com/processlogin.4n6', data = {"username":"{}".format(user), "password":"{}".format(password)}, headers=headers)
        if "NO BOTS! NO SCRAPERS!" not in respAuth.text:
            start = 0
            parser = MyHTMLParser()

            while not parser.stop:
                resp = requests.post('https://virusshare.com/search.4n6', data = {'search':'linux', 'start':'{}'.format(start)}, headers=headers)

                body = resp.text

                parser.feed(body)

                start += 20
        else:
            raise Exception("Error during authentication to VirusShare.")
    else:
        raise Exception("Error, VirusShare is not available (status {}).".format(respGetVS.status_code))