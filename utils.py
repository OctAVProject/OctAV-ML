# coding: utf-8

from tempfile import mkstemp
from html.parser import HTMLParser
from datetime import datetime

import re
import shutil
import config
import zipfile
import io
import requests
import os
import logging

REPO_PATH = 'files/'
MALWARES_DIR = REPO_PATH + "malwares/"

_logger = logging.getLogger(config.UPDATER_LOGGER_NAME)

def sed_in_place(pattern, replace, source):
    """Read file and replace pattern string by replace string"""

    fin = open(source, 'r')

    fd, name = mkstemp()
    fout = open(name, 'w')

    for line in fin:
        out = re.sub(pattern, replace, line)
        fout.write(out)

    fin.close()
    fout.close()

    shutil.move(name, source)


def remove_duplicate_domain_names():
    with open("{}listIpAndDomains.csv".format(REPO_PATH), "r") as mdlfile:
        mdlcontent = csv.reader(csvfile, delimiter=',', quotechar='"')

    with open("{}justdomains".format(REPO_PATH), "r") as mdfile:
        mdcontent = mdfile.read()

    for domain_name in mdlcontent:
        if mdlcontent.row[1] in mdcontent:
            sed_in_place(mdlcontent.row[1] + "\n", "", "{}justdomains".format(REPO_PATH))

            
def _store_ssdeep_hash(path):
    """Calculate ssdeep for file at path and store it in ssdeep file."""

    if not os.path.isdir(REPO_PATH):
        os.makedirs(REPO_PATH)

    if not os.path.isfile("{}ssdeep.txt".format(REPO_PATH)):
        file = open("{}ssdeep.txt".format(REPO_PATH), "w")
        file.close()

    ssdeep_hash = ssdeep.hash_from_file(path)
    with open("{}ssdeep.txt".format(REPO_PATH), "r+") as ssdeep_file:
        lines = ssdeep_file.readlines()
        if ssdeep_hash not in lines:
            ssdeep_file.write("{}\n".format(ssdeep_hash))


class VirusShareHTMLParser(HTMLParser):

    def __init__(self, headers):
        HTMLParser.__init__(self)
        self.headers = headers
        self.in_table = False
        self.in_a = False
        self.date_in_next = False
        self.out_of_a = False
        self.dl_url = ""
        self.stop = False
        self.ignore = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        elif tag == "a" and self.in_table and not self.dl_url:
            end_of_url = attrs[0][1]
            self.dl_url = "https://virusshare.com/{}".format(end_of_url)
            if end_of_url.split("=")[1] in os.listdir(MALWARES_DIR):
                self.ignore = True

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False

    def handle_data(self, data):
        if "VirusShare info last updated" in data and not self.stop:
            date = data.split("updated ")[1]
            date = date.split(" UTC")[0]
            date_t = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            date_base = config.getstr("sync", "last_sync_date")
            date_base = datetime.strptime(date_base, "%Y-%m-%d %H:%M:%S")
            if not self.ignore:
                if date_base < date_t:
                    resp = requests.get(self.dl_url, headers=self.headers)
                    zip_file = zipfile.ZipFile(io.BytesIO(resp.content))
                    status = resp.status_code
                    if status == 200:
                        zip_file.extractall(MALWARES_DIR, pwd=str.encode("infected"))
                        _store_ssdeep_hash("{}{}".format(MALWARES_DIR, zip_file.namelist()[0]))
                        _logger.debug("Download {}".format(zip_file.namelist()[0]))
                    else:
                        raise Exception("Error during file downloading (status {}).".format(resp.status_code))
                else:
                    _logger.debug("Stopping...")
                    self.stop = True
            else:
                _logger.debug("Ignored, already downloaded")
                self.ignore = False

            self.out_of_a = False
            self.dl_url = ""
            self.date_in_next = False