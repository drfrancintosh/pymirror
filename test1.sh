curl -X POST "http://localhost:8080/command" \
  -H "Content-Type: application/json" \
  -d '{"event":"AlertEvent", "header": "WOWSA!", "body":"Hey Kayla, it is going to be 100 degrees today. Stay hydrated!", "footer": "Stay safe!", "timeout": 6000}'

