#!/bin/python
# coding: utf-8

import requests
import os
import re
import config

VIRUS_SHARE_BASE_URL = "https://virusshare.com/hashes/VirusShare_"
MDL_URL = "http://www.malwaredomainlist.com/mdlcsv.php"


# TODO : REMOVE DUPLICATES WITHOUT OVERLOADING THE MEMORY. Bloom filter ?


def sync_md5_hashes():

    try:
        os.mkdir("files/hashes")
    except FileExistsError:
        pass

    file_number_to_download = int(config.get("sync", "lastHashesFileDownloaded")) + 1

    while True:
        file_number_to_download_string = str(file_number_to_download).zfill(5)
        result = requests.get(VIRUS_SHARE_BASE_URL + file_number_to_download_string + ".md5")

        # code 404 means we have reached the end of what we need to download
        if result.status_code == 404:
            break

        elif result.status_code != 200:
            raise Exception("Unusual error code ({}).".format(result.status_code))

        body = result.text
        body = re.sub(r'#.*\n?', '', body, flags=re.MULTILINE)

        with open("files/hashes/{}.md5".format(file_number_to_download_string), "w") as hash_file:
            hash_file.write(body)

        print("DOWNLOADED:", result.url)

        config.update("sync", "lastHashesFileDownloaded", file_number_to_download)
        file_number_to_download += 1


def sync_mdl_ips_and_domains():

    result = requests.get(MDL_URL)

    if result.status_code != 200:
        print("Can't download Malware Domain List, remote server down ?")
        return

    with open("files/listIpAndDomains.csv", "a") as listDomainFile:
        listDomainFile.write(result.text)
