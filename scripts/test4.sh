curl -X POST "http://localhost:8080/command" \
  -H "Content-Type: application/json" \
  -d '{"event":"AlertEvent", "header": "", "body":null, "footer": null, "timeout": 6000}'

