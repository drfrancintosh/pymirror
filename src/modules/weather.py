# weather.py
# https://openweathermap.org/api/one-call-3#current

import requests
import json
from datetime import datetime
from types import SimpleNamespace
from dataclasses import dataclass
from pymirror import PMCard
from events import AlertEvent


@dataclass
class WeatherData:
    lat: str = "37.5050"
    lon: str = "-77.6491"
    appid: str = ""
    exclude: str = "minutely"
    units: str = "imperial"
    lang: str = "english"


class OpenWeatherMap:
    def __init__(self):
        self.base_url = "https://api.openweathermap.org/data/3.0/onecall?"

    def fetch(self, args: WeatherData):
        response = requests.get(self.base_url, params=args.__dict__)
        if response.ok:
            # Parse the JSON response into a dictionary
            return response.json()
        else:
            print(
                f"Error fetching weather data: {response.status_code} - {response.text}"
            )
            return {"error": "error"}


def _paragraph_fix(text: str) -> str:
    results = []
    paragraphs = text.split("\n\n")
    for paragraph in paragraphs:
        lines = paragraph.split("\n")
        paragraph = " ".join(line.strip() for line in lines)
        results.append(paragraph)
    return "\n\n".join(results)


class Weather(PMCard):
    def __init__(self, pm, config):
        super().__init__(pm, config)
        self._weather = config.weather
        self.weather_data = WeatherData(**self._weather.weather_data.__dict__)
        self.refresh_minutes = self._weather.refresh_minutes
        self.degrees = (
            self._weather.degrees if hasattr(self._weather, "degrees") else "\u00b0F"
        )  # Default to Fahrenheit
        self.datetime_format = (
            self._weather.datetime_format
            if hasattr(self._weather, "datetime_format")
            else "%I:%M:%S %p"
        )
        self.timer.set_timeout(1)  # refresh right away
        self.weather_response = None
        self.weather_api = OpenWeatherMap()
        self.update("", "", "")  # Initialize with empty strings

    def exec(self) -> bool:
        is_dirty = super().exec()
        if not self.timer.is_timedout():
            return is_dirty # early exit if not timed out
        self.timer.set_timeout(self.refresh_minutes * 60 * 1000)
        self.weather_response = self.weather_api.fetch(self.weather_data)
        print(f"Weather response: {self.weather_response}")  # Debugging line
        w = SimpleNamespace(**self.weather_response.get("current"))
        # convert w.current.dt to a datetime object
        dt_str = datetime.fromtimestamp(w.dt).strftime(self.datetime_format)
        self.update(
            "WEATHER",
            f"{w.temp}{self.degrees}\n{w.humidity} %\n{w.feels_like}{self.degrees}",
            dt_str,
        )

        if self.weather_response.get("alerts"):
            alerts = self.weather_response["alerts"]
            if alerts:
                alert = alerts[0]
                event = {
                    "event": "WeatherAlertEvent",
                    "header": alert["event"],
                    "body": f"{_paragraph_fix(alert['description'])}",
                    "footer": "Expires: "
                    + datetime.fromtimestamp(alert["end"]).strftime(
                        self.datetime_format
                    ),
                    "timeout": 0,
                }
                self.publish_event(event)

        self.weather_response = None  # Clear response after rendering
        return True # state changed
