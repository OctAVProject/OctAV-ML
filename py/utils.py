# coding: utf-8

from tempfile import mkstemp
from html.parser import HTMLParser
from datetime import datetime
from keras.preprocessing.sequence import pad_sequences

import re
import shutil
import zipfile
import io
import requests
import os
import logging
import ssdeep
import numpy as np

import py.config as config
from py.syscalls import SYSCALLS

_logger_up = logging.getLogger(config.UPDATER_LOGGER_NAME)
_logger_tf = logging.getLogger(config.TENSORFLOW_LOGGER_NAME)

def _load_report(filepath, regex=r"\.*?api.: .([a-z_0-9]+)"):
    syscall_seq = []

    with open(filepath, "r") as f:
        content = f.read()
        for m in re.finditer(regex, content):
            syscall = m.group(1)
            if syscall in SYSCALLS:
                syscall_num = SYSCALLS[syscall]
                if syscall_num < config.MAX_SYSCALL_NUM:
                    syscall_seq.append(syscall_num)

    one_hot_encoded = np.eye(config.MAX_SYSCALL_NUM)[syscall_seq]
    seq = np.concatenate((one_hot_encoded, np.zeros((1, config.MAX_SYSCALL_NUM))))

    return seq


def load_train_dataset():
    """Read strace files and malwares reports to create a dataset with one-hot-encoded datas."""
    seqs, targs = [], []

    for subdir, dirs, files in os.walk("{}dataset_train/legits".format(config.DATASETS_DIR)):
        for file in files:
            if file.endswith(".strace") or file.endswith(".json"):
                filepath = os.path.join(subdir, file)                
                _logger_tf.debug("Loading {}".format(filepath))

                if file.endswith(".strace"):
                    seq = _load_report(filepath, r"([a-z_0-9]+)\(")
                else:
                    seq = _load_report(filepath)

                seqs.append(seq)
                targs.append(0)

    for subdir, dirs, files in os.walk("{}dataset_train/malwares".format(config.DATASETS_DIR)):
        for file in files:
            if file.endswith(".strace") or file.endswith(".json"):
                filepath = os.path.join(subdir, file)                
                _logger_tf.debug("Loading {}".format(filepath))

                if file.endswith(".strace"):
                    seq = _load_report(filepath, r"([a-z_0-9]+)\(")
                else:
                    seq = _load_report(filepath)

                seqs.append(seq)
                targs.append(1)


    indices = np.arange(len(seqs))
    np.random.shuffle(indices)

    split_index = int(len(seqs) * config.VALIDATION)

    train_indices = indices[split_index:]
    valid_indices = indices[:split_index]

    X_train = [seqs[i] for i in train_indices]
    X_valid = [seqs[i] for i in valid_indices]

    Y_train = np.array([targs[i] for i in train_indices])
    Y_valid = np.array([targs[i] for i in valid_indices])

    X_train = pad_sequences(X_train)
    X_valid = pad_sequences(X_valid)

    return (X_train, Y_train) , (X_valid, Y_valid)


def load_check_dataset():
    seqs, targs = [], []

    for subdir, dirs, files in os.walk("{}dataset_check/legits".format(config.DATASETS_DIR)):
        for file in files:
            if file.endswith(".strace") or file.endswith(".json"):
                filepath = os.path.join(subdir, file)                
                _logger_tf.debug("Loading {}".format(filepath))

                if file.endswith(".strace"):
                    seq = _load_report(filepath, r"([a-z_0-9]+)\(")
                else:
                    seq = _load_report(filepath)

                seqs.append(seq)
                targs.append(0)

    for subdir, dirs, files in os.walk("{}dataset_check/malwares".format(config.DATASETS_DIR)):
        for file in files:
            if file.endswith(".strace") or file.endswith(".json"):
                filepath = os.path.join(subdir, file)                
                _logger_tf.debug("Loading {}".format(filepath))

                if file.endswith(".strace"):
                    seq = _load_report(filepath, r"([a-z_0-9]+)\(")
                else:
                    seq = _load_report(filepath)
                seq_len = seq.shape[0]

                seqs.append(seq)
                targs.append(1)

    X_check = pad_sequences(seqs)
    Y_check = np.array([targs[i] for i in range(len(targs))])

    return X_check, Y_check

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
    with open("{}listIpAndDomains.csv".format(config.REPOFILES_PATH), "r") as mdlfile:
        mdlcontent = csv.reader(csvfile, delimiter=',', quotechar='"')

    with open("{}justdomains".format(config.REPOFILES_PATH), "r") as mdfile:
        mdcontent = mdfile.read()

    for domain_name in mdlcontent:
        if mdlcontent.row[1] in mdcontent:
            sed_in_place(mdlcontent.row[1] + "\n", "", "{}justdomains".format(config.REPOFILES_PATH))

            
def _store_ssdeep_hash(path):
    """Calculate ssdeep for file at path and store it in ssdeep file."""

    if not os.path.isdir(config.REPOFILES_PATH):
        os.makedirs(config.REPOFILES_PATH)

    if not os.path.isfile("{}ssdeep.txt".format(config.REPOFILES_PATH)):
        file = open("{}ssdeep.txt".format(config.REPOFILES_PATH), "w")
        file.close()

    ssdeep_hash = ssdeep.hash_from_file(path)
    with open("{}ssdeep.txt".format(config.REPOFILES_PATH), "r+") as ssdeep_file:
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
            if end_of_url.split("=")[1] in os.listdir(config.MALWARES_DIR):
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
                        zip_file.extractall(config.MALWARES_DIR, pwd=str.encode("infected"))
                        _store_ssdeep_hash("{}{}".format(config.MALWARES_DIR, zip_file.namelist()[0]))
                        _logger_up.debug("Download {}".format(zip_file.namelist()[0]))
                    else:
                        raise Exception("Error during file downloading (status {}).".format(resp.status_code))
                else:
                    _logger_up.debug("Stopping...")
                    self.stop = True
            else:
                _logger_up.debug("Ignored, already downloaded")
                self.ignore = False

            self.out_of_a = False
            self.dl_url = ""
            self.date_in_next = False