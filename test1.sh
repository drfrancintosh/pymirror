curl -X POST "http://localhost:8080/command" \
  -H "Content-Type: application/json" \
  -d '{"name":"weather_alert", "heading": "WOWSA!", "message":"Hey Kayla, it is going to be 100 degrees today. Stay hydrated!", "footer": "Stay safe!", "timeout": 6000}'

