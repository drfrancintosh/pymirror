#!/bin/bash

if [ $# -eq 0 ]; then
    CONFIG="./configs/config.json"
else
    CONFIG="./configs/$1"
fi

# Create a new process group and redirect everything
exec > src/pmserver/static/output.log 2>&1
PYTHONPATH=src python3 -u -m pymirror.pymirror --config "$CONFIG"