#!/bin/python
# coding: utf-8

"""Downloader module for Octav updater.

    Module used to download and save file containing hashes of malwares,
    malicious ips and domain names.
"""

# LIBRARIES
import requests
import argparse
import os
import re
import io
import zipfile

import configmanager

# Code

HOME_DIR = "/etc/octav"
FILE_DIR = HOME_DIR + '/files/'

cm = None


class Downloader(object):
    """File management for Octav.

        Download new signature files and untrusted domain name and ips.
    """

    def __init__(self):
        """
            Initialize the downloader with urls for public lists and
            directories location to store the new files.
        """
        global cm
        self._cm = configmanager.ConfigurationManager()
        cm = self._cm

        self._vs_hashes_baseurl = "https://virusshare.com/hashes/VirusShare_"
        self._mdl_domains_url = "http://www.malwaredomainlist.com/mdlcsv.php"
        self._md_domains_url = "http://www.malware-domains.com/files/justdomains.zip"
        self._md5_hashes_dir = FILE_DIR + "md5_hashes/"
        self._ip_and_domain_dir = FILE_DIR + "malicious_domains_and_ips/"

    def sync_md5_hashes(self):
        """
            Download new hash files from virusshare.com.
        """
        if not os.path.isdir(self._md5_hashes_dir):
            os.makedirs(self._md5_hashes_dir)

        file_number = int(self._cm.sync.last_hashes_file_downloaded) + 1
        status = 200

        while int(status) == 200 and file_number < 1:
            file_number_s = str(file_number).zfill(5)
            url = self._vs_hashes_baseurl + file_number_s + ".md5"
            status, body = self._download_file(url)

            body = re.sub(r'#.*\n?', '', body, flags=re.MULTILINE)

            if int(status) == 200:
                with open("{}{}.md5".format(
                        self._md5_hashes_dir,
                        file_number_s), "w") as hashes_fp:
                    hashes_fp.write(body)

            file_number += 1
        self._cm.update_config("last_hashes_file_downloaded",
                                str(file_number-1), "sync")

    def sync_mdl_ips_and_domains(self):
        """
            Download new malicious domain name lists from
            malwaredomainlist.com.
        """
        if not os.path.isdir(self._ip_and_domain_dir):
            os.makedirs(self._ip_and_domain_dir)

        if(self._cm.sync.first_sync_done_from_mdl) == "no":
            status, body = self._download_file(self._mdl_domains_url)
            if int(status) == 200:
                with open("{}listIpAndDomains.csv".format(
                        self._ip_and_domain_dir), "a") as list_domains_fp:
                    list_domains_fp.write(body)
            self._cm.update_config("first_sync_done_from_mdl", "yes", "sync")

    def sync_md_domains(self):
        """
            Download new malicious domain name lists from
            malwaredomainlist.com.
        """
        if not os.path.isdir(self._ip_and_domain_dir):
            os.makedirs(self._ip_and_domain_dir)

        status, zip_file = self._download_zipfile(self._md_domains_url)
        if int(status) == 200:            
            zip_file.extractall("{}".format(self._ip_and_domain_dir))

    def _download_file(self, url):
        """
            Download a file using requests module.

            :param url: url to request
            :type url: str

            :Example:
            >>> self._download_file(
                "http://www.malwaredomainlist.com/mdlcsv.php")
        """
        print(url)
        resp = requests.get(url)
        return resp.status_code, resp.text

    def _download_zipfile(self, url):
        """
            Download a zip archive using requests module.

            :param url: url to request
            :type url: str

            :Example:
            >>> self._download_zipfile(
                "http://www.malware-domains.com/files/justdomains.zip")
        """
        print(url)
        resp = requests.get(url)
        zip_file = zipfile.ZipFile(io.BytesIO(resp.content))
        return resp.status_code, zip_file
