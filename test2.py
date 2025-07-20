from flask import json
import requests
## https://api.windy.com/point-forecast/docs#swagger-ui-container

def fetch_point_forecast(api_key, lat, lon, model="namConus",
                         parameters=None, levels=None):
    url = "https://api.windy.com/api/point-forecast/v2"
    headers = {"Content-Type": "application/json"}
    body = {
        "lat": lat,
        "lon": lon,
        "model": model,
        "parameters": parameters or ["wind", "windGust", "temp", "lclouds"],
        "levels": levels or ["surface"],
        "key": api_key
    }
    resp = requests.post(url, json=body, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    API_KEY = "a1W3RHPBJySt1idTxMOrQKpzRebxoIv0"
    lat, lon = 37.4971, -77.7305  # Example: Midlothian, VA area
    data = fetch_point_forecast(API_KEY, lat, lon)
    print(json.dumps(data, indent=2))  # ts, units, wind-surface, temp-surface, etc.
