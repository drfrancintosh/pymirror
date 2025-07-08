#!/bin/bash

if [ $# -eq 0 ]; then
    CONFIG="./configs/config.json"
else
    CONFIG="./configs/$1"
fi

PYTHONPATH=src python3 -u -m pymirror.pymirror --config "$CONFIG" 2>&1 > src/pmserver/static/output.log
