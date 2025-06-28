curl -X POST "http://localhost:8080/command" \
  -H "Content-Type: application/json" \
  -d '{"event":"AlertEvent", "header": "", "body":"Missing Header", "footer": "Stay safe!", "timeout": 6000}'

