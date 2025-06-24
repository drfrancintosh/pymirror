# weather.py
# https://openweathermap.org/api/one-call-3#current

import requests
import json
from types import SimpleNamespace
from dataclasses import dataclass, fields
from pymirror.pmmodule import PMModule
import copy

@dataclass
class WeatherData:
	lat: str
	lon: str
	appid: str
	exclude: str #current,minutely,hourly,daily,alerts
	units: str #standard, metric, imperial
	lang: str

class OpenWeatherMap:
	def __init__(self):
		self.base_url = "https://api.openweathermap.org/data/3.0/onecall?"

	def fetch(self, args: WeatherData):
		response = requests.get(self.base_url, params=args.__dict__)
		if response.ok:
			return response.json()
		else:
			return {"error": "error"}


class Weather(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.weather_data = WeatherData(**moddef.config.__dict__)
		self.refresh_minutes = 5
		self.set_timeout(1) # refresh right away
		self.weather_response = None
		self.weather_api = OpenWeatherMap()

	def render(self):
		if not self.weather_response: return 0
		gfx = copy.copy(self.gfx)
		degrees = "\u00B0F"  # Degree symbol for Fahrenheit
		x = gfx.x0
		y = gfx.y0
		w = SimpleNamespace(**self.weather_response["current"])
		text = self.screen.text
		text_box = self.screen.text_box
		# text_box(self, gfx, msg, x0=None, y0=None, x1=None, y1=None, valign="center", halign="center"):
		# text(gfx, f"Temp: {w.temp}F\nHumidity: {w.humidity}\nFeels Like: {w.feels_like}F\n{w.weather[0].descripition}", x, y)
		text_box(gfx, "Weather", valign="top")
		gfx.text_color = (0,0,0)
		text(gfx, f"{w.temp}{degrees}", x, y + gfx.font_size)
		text(gfx, f"{w.humidity} mb", x, y + gfx.font_size * 2)
		text(gfx, f"{w.feels_like}{degrees}", x, y + gfx.font_size * 3)
		self.weather_response = None  # Clear response after rendering
		return 1

	def exec(self):
		if self.is_timedout():
			self.weather_response = self.weather_api.fetch(self.weather_data)
			print(json.dumps(self.weather_response, indent=2))
			self.set_timeout(self.refresh_minutes * 60 * 1000)
		return self.render()

	def onEvent(self, event):
		pass			
			
		
def main():
	parms = WeatherData(37.5037, -77.6428, "appid", "minutely,hourly,daily", "imperial", "english")	
	weather = OpenWeatherMap()
	current = weather.fetch(parms)
	print(json.dumps(current, indent=2))

if __name__ == "__main__":
	main()

