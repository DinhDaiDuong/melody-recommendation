#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y build-essential python3-dev gcc

# Install Python packages
pip install --upgrade pip
pip install wheel
pip install cython==0.29.24
pip install -r requirements.txt 