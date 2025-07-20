#!/bin/bash

if [ $# -ne 2 ]; then
  echo "Usage: $0 <host> <body>"
  exit 1
fi

HOST="$1"
BODY="$2"
date=`date +"%Y-%m-%d %H:%M:%S"`
curl -X POST "http://$HOST:8080/event" \
  -H "Content-Type: application/json" \
  -d "{\"event\":\"AlertEvent\", \"header\": \"Alert\", \"body\": \"$BODY\", \"footer\": \"$date\", \"timeout\": 5000}"