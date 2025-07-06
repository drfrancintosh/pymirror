# weather.py
# https://openweathermap.org/api/one-call-3#current

import requests
import json
from datetime import datetime
from types import SimpleNamespace
from dataclasses import dataclass
from pymirror.pmcard import PMCard
from events import AlertEvent
from pymirror.pmwebapi import PMWebApi

@dataclass
class OpenWeatherMapConfig:
    lat: str = "37.5050"
    lon: str = "-77.6491"
    appid: str = ""
    exclude: str = "minutely"
    units: str = "imperial"
    lang: str = "english"

@dataclass
class WeatherConfig:
    url: str
    cache_file: str  = None
    cache_timeout_secs: int = 3600  # Default cache timeout in seconds
    refresh_minutes: int = 15
    degrees: str = "°F"
    datetime_format: str = "%I:%M:%S %p"
    lat: str = "37.5050"
    lon: str = "-77.6491"
    appid: str = ""
    exclude: str = "minutely"
    units: str = "imperial"
    lang: str = "english"

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
        self._api = WeatherConfig(**self._weather.__dict__)
        self.timer.set_timeout(1)  # refresh right away
        self.weather_response = None
        self.api = PMWebApi(self._api.url, self._api.cache_file, self._api.cache_timeout_secs)
        self.owm_config = OpenWeatherMapConfig(
            lat=self._api.lat,
            lon=self._api.lon,
            appid=self._api.appid,
            exclude=self._api.exclude,
            units=self._api.units,
            lang=self._api.lang
        )
    def exec(self) -> bool:
        is_dirty = super().exec()
        if not self.timer.is_timedout():
            return is_dirty # early exit if not timed out
        self.timer.set_timeout(self._weather.refresh_minutes * 60 * 1000)
        self.weather_response = self.api.get_json(self.owm_config.__dict__)
        print(f"Weather response: {self.weather_response}")  # Debugging line
        w = SimpleNamespace(**self.weather_response.get("current"))
        # convert w.current.dt to a datetime object
        dt_str = datetime.fromtimestamp(w.dt).strftime(self._weather.datetime_format)
        self.update(
            "WEATHER",
            f"{w.temp}{self._weather.degrees}\n{w.humidity} %\n{w.feels_like}{self._weather.degrees}",
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
                    "footer": f"Expires: {datetime.fromtimestamp(alert['end']).strftime(self.datetime_format)}",
                    "timeout": 0
                }
                print(f"Publishing weather alert event: {event['event']}")
                self.publish_event(event)

        self.weather_response = None  # Clear response after rendering
        return True # state changed
