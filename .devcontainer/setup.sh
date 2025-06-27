#!/usr/bin/env bash
set -e

# 1) System build tools + distutils for numpy/mmh3
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
    build-essential gcc python3-dev python3-distutils git \
 && sudo rm -rf /var/lib/apt/lists/*

# 2) Python packaging front-end for PEP517
pip install --upgrade pip setuptools wheel build

# 3) Pin numpy to avoid 3.12 issues
# (edit your requirements.txt accordingly)
pip install -r requirements.txt
