curl -X POST "http://rpi02.local:8080/event" \
  -H "Content-Type: application/json" \
  -d '{"event":"PyMirrorEvent", "debug": false}'

