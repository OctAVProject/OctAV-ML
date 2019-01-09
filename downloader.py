#!/bin/python
# coding: utf-8

### LIBRARIES
import requests
import argparse
import os
import re

import configManager

### Code

cm = None

class Downloader(object):
    """File management for Octav.

    Download new signature files and untrusted domain name
    """

    def __init__(self):
        global cm
        self.cm = configManager.ConfigurationManager()
        cm = self.cm

        self.lastHashesFileDownloaded = self.cm.sync.lastHashesFileDownloaded
        self.virusShareHashesBaseURL = "https://virusshare.com/hashes/VirusShare_"
        self.md5hashes_dir = self.cm.files_dir + "md5_hashes/"
        self.ipanddomain_dir = self.cm.files_dir + "malicious_domains_and_ips/"

    def convertFileNumberToString(self, fileNumber):
        fileNumberString = str(fileNumber)
        while len(fileNumberString) < 5:
            fileNumberString = "0" + fileNumberString
        return fileNumberString

    def syncMD5Hashes(self):
        if not os.path.isdir(self.md5hashes_dir):
            os.makedirs(self.md5hashes_dir)

        fileNumber = int(self.lastHashesFileDownloaded) + 1
        status = 200

        while int(status) == 200 and fileNumber < 2:
            fileNumberString = self.convertFileNumberToString(fileNumber)
            url = self.virusShareHashesBaseURL + fileNumberString + ".md5"
            status, body = self.downloadFile(url)

            body = re.sub(r'#.*\n?', '', body, flags=re.MULTILINE)

            if int(status) == 200:
                with open("{}{}.md5".format(self.md5hashes_dir, fileNumberString), "w") as hashFile:
                    hashFile.write(body)

            fileNumber += 1
        self.cm.updateConfig("lastHashesFileDownloaded", str(fileNumber-1), "sync")

    def syncMDLIpAndDomain(self):
        if not os.path.isdir(self.ipanddomain_dir):
            os.makedirs(self.ipanddomain_dir)

        url = "http://www.malwaredomainlist.com/mdlcsv.php"
        status, body = self.downloadFile(url)
        if int(status) == 200: 
            with open("{}listIpAndDomains.csv".format(self.ipanddomain_dir), "a") as listDomainFile:
                listDomainFile.write(body)

    def downloadFile(self, url):
        print(url)
        resp = requests.get(url)        
        return resp.status_code, resp.text

