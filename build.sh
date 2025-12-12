#! /bin/bash

# Build the project
echo "Building the project..."
rm -rf dist
#python3 build.py
poetry build
# local install
python3 -m pip install --force-reinstall dist/*.whl
