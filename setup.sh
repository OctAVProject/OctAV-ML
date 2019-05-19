#!/bin/bash

virtualenv -p python3 venv

source venv/bin/activate

pip3 install keras gitpython requests ssdeep hyperopt hyperas

pip3 install tensorflow
pip3 install tensorflow-gpu

deactivate