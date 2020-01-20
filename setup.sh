#!/bin/bash
set -e

cd "$(dirname "$0")"  # Set working directory to script's directory

if ! [ -d logs ]; then
    mkdir logs
fi

if ! [ -d "files" ];then
    echo "Cloning OctAV-Files repository"
    if git clone git@github.com:OctAVProject/OctAV-Files.git files &> /dev/null; then
        echo "Error: please install git"
        exit 1
    fi
fi

if ! [ -d "files" ];then
    echo "Cloning OctAV-Dataset-Generator repository"
    if git clone https://github.com/OctAVProject/OctAV-Dataset-Generator.git &> /dev/null; then
        echo "Error: please install git"
        exit 1
    else
        mv OctAV-Dataset-Generator/dataset .
        mv OctAV-Dataset-Generator/sandbox .
        mv OctAV-Dataset-Generator/requirements.txt requirements_dataset_generator.txt
        rm -r OctAV-Dataset-Generator
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

echo "Installing python dependencies in virtual environment..."
pip install -r requirements.txt &>> logs/setup.log
pip install -r requirements_dataset_generator.txt &>> logs/setup.log

read -p "Do you have a gpu? [Y/N] " yn
case $yn in
    [Yy]* ) read -p "You need to install CUDA_9 to work with tensorflow with a GPU, do you have it ? [Y/N] " yn
            case $yn in
                 [Yy]*) pip install tensorflow-gpu==1.9.0 &>> logs/setup.log;;
                 [Nn]*) exit 1;;
            esac;;
    [Nn]* ) pip install tensorflow==2.0 &>> logs/setup.log;;
    * ) echo "Please answer yes or no.";;
esac

deactivate

echo -e "\nNow all you have to do to use the manager is to join the virtual environment :"
echo -e ". venv/bin/activate\n"

echo "Run the manager :"
echo -e "python manager.py -u VIRUSSHARE_USER [-l LOGLEVEL] [ -m | -s ]"
