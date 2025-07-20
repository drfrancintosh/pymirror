#!/bin/bash

if [ $# -ne 3 ]; then
  echo "Usage: $0 <host> <key> <value>"
  exit 1
fi

HOST="$1"
KEY="$2"
VALUE="$3"

curl -X POST "http://$HOST:8080/event" \
  -H "Content-Type: application/json" \
  -d "{\"event\":\"PyMirrorEvent\", \"$KEY\": \"$VALUE\"}"