curl -X POST "http://rpi02.local:8080/event" \
  -H "Content-Type: application/json" \
  -d '{"event":"WeatherAlertEvent", "header": "Weather Alert", "body":"This is an alert from the national association of weather forecasters.", "footer": "2025-06-30 @ 16:05:24", "timeout": 6000}'

