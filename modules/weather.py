# weather.py
# https://openweathermap.org/api/one-call-3#current

import requests
import json
from types import SimpleNamespace
from dataclasses import dataclass, fields
from pymirror.pmmodule import PMModule

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
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self.weather_data = WeatherData(**config.weather_data.__dict__)
		self.refresh_minutes = 5
		self.set_timeout(1) # refresh right away
		self.weather_response = None
		self.weather_api = OpenWeatherMap()

	def render(self):
		if not self.weather_response: return
		gfx = self.gfx
		x = gfx.x0
		y = gfx.y0
		print(self.weather_response)
		w = SimpleNamespace(**self.weather_response["current"])
		text = self.screen.text
		# text(gfx, f"Temp: {w.temp}F\nHumidity: {w.humidity}\nFeels Like: {w.feels_like}F\n{w.weather[0].descripition}", x, y) 
		text(gfx, f"Temp: {w.temp}F\nHumidity: {w.humidity}\nFeels Like: {w.feels_like}F", x, y) 

	def exec(self):
		if self.is_timedout():
			self.weather_response = self.weather_api.fetch(self.weather_data)
			self.set_timeout(self.refresh_minutes * 60 * 1000)
		self.render()
		
	def onEvent(self, event):
		pass			
			
		
def main():
	parms = WeatherData(37.5037, -77.6428, "appid", "minutely,hourly,daily", "imperial", "english")	
	weather = OpenWeatherMap()
	current = weather.fetch(parms)
	print(json.dumps(current, indent=2))

if __name__ == "__main__":
	main()

