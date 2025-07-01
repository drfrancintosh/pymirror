#!/bin/bash

if [ $# -eq 0 ]; then
    CONFIG="./configurations/config.json"
else
    CONFIG="$1"
fi

PYTHONPATH=src python3 -m pymirror.pymirror --config "$CONFIG"
