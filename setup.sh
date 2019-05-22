#!/bin/bash

if ! [ -d "files" ];then
    echo "Cloning OctAV-Files repository"
    if git clone git@github.com:OctAVProject/OctAV-Files.git files &> /dev/null; then
        echo "Error: please install git"
        exit 1
    fi
fi

if ! [ -d "venv" ]; then
    echo "Creating virtual environment..."
    if ! virtualenv -p python3 venv &> logs/setup.log; then
        echo "Error: please install virtualenv."
        exit 1
    fi
fi

source venv/bin/activate

echo "Installing git requests ssdeep and tensorflow in virtual environment..."

pip3 install keras gitpython requests ssdeep &>> logs/setup.log

read -p "Do you have a gpu? [Y/N] " yn
case $yn in
    [Yy]* ) read -p "You need to install CUDA to work with tensorflow with a GPU, do you have it ? [Y/N] " yn
            case $yn in
                 [Yy]*) pip3 install tensorflow-gpu &>> logs/setup.log;;
                 [Nn]*) exit 1;;
            esac;;
    [Nn]* ) pip3 install tensorflow &>> logs/setup.log;;
    * ) echo "Please answer yes or no.";;
esac

deactivate

echo "\nNow all you have to do to use the manager is to join the virtual environment :"
echo -e ". venv/bin/activate\n"

echo "Run the manager :"
echo -e "python manager.py -u VIRUSSHARE_USER [-l LOGLEVEL] [ -m | -s ]"