#!/bin/bash

set -e

echo "Setting up venv"
python3.12 -m venv ./.venv/
echo "Activating venv"
. .venv/bin/activate
echo "Installing dependencies"
pip install piptools
pip install -r ./requirements.txt
