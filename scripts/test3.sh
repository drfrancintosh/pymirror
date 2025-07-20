curl -X POST "http://localhost:8080/command" \
  -H "Content-Type: application/json" \
  -d '{"event":"AlertEvent", "header": "", "body":"Missing Header and footer", "footer": null, "timeout": 6000}'

