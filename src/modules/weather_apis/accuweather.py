from dataclasses import dataclass
from datetime import datetime
from logging import config
from pymirror.pmwebapi import PMWebApi
from pymirror.utils import SafeNamespace
from .pmweatherdata import PMWeatherAlert, PMWeatherCurrent, PMWeatherDaily, PMWeatherData, PMWeatherSummary

@dataclass 
class AccuWeatherParams:
    apikey: str = ""
    lat: str = "37.5050"
    lon: str = "-77.6491"
    language: str = "en-us"
    units: str = "imperial"

@dataclass
class AccuWeatherConfig:
    name: str = "AccuWeather"
    url: str = "http://dataservice.accuweather.com/currentconditions/v1/"
    cache_file: str  = "./caches/weather.json"
    cache_timeout_secs: int = 3600  # Default cache timeout in seconds

class AccuWeatherLocationConfig:
    name: str = "AccuWeather Location"
    url: str = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
    cache_file: str  = "./caches/location.json"
    cache_timeout_secs: int = 3600 * 24  # Default cache timeout in seconds

class AccuWeatherApi(PMWebApi):
    """
    A wrapper for the AccuWeather API that uses PMWebApi.
    This is a convenience function to create an instance of PMWebApi with the AccuWeatherConfig.
    """
    def __init__(self, config: SafeNamespace):
        self.config = AccuWeatherConfig()
        super().__init__(self.config.url, self.config.cache_file, self.config.cache_timeout_secs)
        print(f"AccuWeatherApi initialized with params: {config}")
        self.params = AccuWeatherParams(**config.__dict__)
        self.location_key = None
    
    def get_weather_data(self, params = None) -> PMWeatherData:
        """
        Fetches weather data from the AccuWeather API.
        If params are provided, they will be used in the request.
        """
        self.get_location_data() ## get the location key if not already set
        params = {
            "_resource_id": self.location_key,
            "apikey": self.params.apikey,
            "details": True,
            "language": self.params.language,
        }
        response = self.get_json(params)
        if not response: return None
        r = SafeNamespace(**(response[0]))
        units = self.params.units.capitalize()
        c = {
            "dt": datetime.fromisoformat(r.LocalObservationDateTime).timestamp(),
            "temp":  r.Temperature[units].Value,
            "feels_like":  r.RealFeelTemperature[units].Value,
            "pressure":  r.Pressure[units].Value,
            "humidity":  r.RelativeHumidity,
            "dew_point":  r.DewPoint[units].Value,
            "uvi":  r.UVIndexFloat,
            "clouds":  r.CloudCover,
            "visibility":  r.Visibility[units].Value,
            "wind_speed":  r.Wind.Speed[units].Value,
            "wind_deg":  r.Wind.Direction.Degrees,
            "wind_gust":  r.WindGust.Speed[units].Value
        }
        d = {
            "dt": int(r.EpochTime),
            "summary": r.WeatherText,
            "temp": {
                "day": c["temp"],
                "min": c["temp"],
                "max": c["temp"],
                "night": c["temp"],
                "eve": c["temp"],
                "morn": c["temp"]
            },
            "feels_like": {
                "day": c["feels_like"],
                "night": c["feels_like"],
                "eve": c["feels_like"],
                "morn": c["feels_like"]
            },
            "pressure": c["pressure"],
            "humidity": c["humidity"],
            "dew_point": c["dew_point"],
            "wind_speed": c["wind_speed"],
            "wind_deg": c["wind_deg"],
            "wind_gust": c["wind_gust"],
            "weather": [PMWeatherSummary(id=1, main=r.WeatherText, description=r.WeatherText, icon="").__dict__],
            "clouds": r.CloudCover,
            "pop": 0.0,
            "rain": 0.0,
            "uvi": c["uvi"]
        }
        w = {
            "lat": float(self.params.lat),
            "lon":  float(self.params.lon),
            "timezone": self.location_data.TimeZone.Name,
            "timezone_offset": self.location_data.TimeZone.GmtOffset * 3600,
            "current":  c,
            "daily":  [d],
            "alerts": None
        }
        print(f"AccuWeatherApi response: {w}")
        weather = PMWeatherData.from_dict(w)
        return weather

    def get_location_data(self) -> str:
        if self.location_key: return self.location_key
        config = AccuWeatherLocationConfig()
        location_api = PMWebApi(config.url, config.cache_file, config.cache_timeout_secs)
        location_data = location_api.get_json({
            "apikey": self.params.apikey,
            "q": f"{self.params.lat},{self.params.lon}",
            "details": "false",
            "toplevel": "false"
        })
        self.location_data = SafeNamespace(**location_data)
        self.location_key = location_data["Key"]
        print(f"AccuWeather location key: {self.location_key}")
        return self.location_key