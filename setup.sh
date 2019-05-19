#!/bin/bash

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    if ! virtualenv -p python3 venv &> setup.log; then
        echo "Error: please install virtualenv."
        exit 1
    fi
fi

source venv/bin/activate

echo "Installing git requests ssdeep and tensorflow in virtual environment..."

pip3 install keras gitpython requests ssdeep

read -p "Do you have a gpu? [Y/N] " yn
case $yn in
    [Yy]* ) pip3 install tensorflow-gpu;;
    [Nn]* ) pip3 install tensorflow;;
    * ) echo "Please answer yes or no.";;
esac

deactivate