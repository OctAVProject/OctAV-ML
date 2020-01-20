# OctAV Updater

## Goals
- Retrieve malicious domains and ips
- Retrieve known hashes
- Perform machine learning
- Keep the `OctAV-Files` repository up to date

## Requirements

You need the following programs to be installed :

- git
- python3.7
- docker-compose
- firejail
- strace
- xvfb

To compile ssdeep library for python on Debian, you also need :

- build-essential
- libffi-dev
- libfuzzy-dev

## Installation

```
$ git clone https://github.com/OctAVProject/OctAV-Manager.git
$ cd OctAV-Manager/
$ ./setup.sh
```

# OctAV Manager

This repository's goal is to load the files repository with data from public lists and with the Machine Learning model for Octav dynamic analysis.

The manager combine 2 components, the manager and the dataset generator.

The first component download data from public lists, train the Machine Learning model and push them on the files repository.

The Octav-Dataset-Generator is cloned into the manager to be used in order to create a dataset used to train the model and push it to the files repository.
More information is available on Octav-Dataset-Generator repository on Github.com.

## Usage

Public lists synchronization

```
$ python -m manager --help
usage: manager.py [-h] [-l {DEBUG,INFO,WARNING,ERROR}] [-m | -c | -s]

OctAV Manager : in charge of updating the repository periodically and 
performing machine learning.

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR}, --log-level {DEBUG,INFO,WARNING,ERROR}
                        Set the log level
  -m, --ml-only         Only perform machine learning.
  -c, --check_model     Only assess model.
  -s, --sync-only       Only perform synchronisation.
```

Ex: `python manager.py -l DEBUG`

```
$ python -m dataset --help
usage: python -m dataset [-h] [--malware-dirs DIRECTORY [DIRECTORY ...]]
                         [--legit-dirs DIRECTORY [DIRECTORY ...]] --db DB_FILE [--overwrite]
                         [--append] [--stats]

This is the dataset builder.

optional arguments:
  -h, --help            show this help message and exit
  --malware-dirs DIRECTORY [DIRECTORY ...]
                        directories of malwares to process
  --legit-dirs DIRECTORY [DIRECTORY ...]
                        directories of legit binaries to process
  --db DB_FILE          sqlite database
  --overwrite           delete the existing database to create a new one
  --append              append results to the existing database
  --stats               prints some stats about the given dataset
```

Ex: `python -m dataset --legit-dirs /bin /sbin /usr/bin --db dataset.db --append --stats`


