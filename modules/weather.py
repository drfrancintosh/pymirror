# weather.py
# https://openweathermap.org/api/one-call-3#current

import os
import requests
import json
import copy
from types import SimpleNamespace
from dataclasses import dataclass
from pymirror.pmmodule import PMModule
from modules.alert import AlertEvent


@dataclass
class WeatherData:
	lat: str = "37.5050"
	lon: str = "-77.6491"
	appid: str = "$OPENWEATHERMAP_API_KEY"
	exclude: str = "minutely"
	units: str = "imperial"
	lang: str = "english"

class OpenWeatherMap:
	def __init__(self):
		self.base_url = "https://api.openweathermap.org/data/3.0/onecall?"

	def fetch(self, args: WeatherData):
		response = requests.get(self.base_url, params=args.__dict__)
		if response.ok:
			return response.json()
		else:
			return {"error": "error"}

def _paragraph_fix(text: str) -> str:
	results = []
	paragraphs = text.split("\n\n")
	for paragraph in paragraphs:
		lines = paragraph.split("\n")
		paragraph = " ".join(line.strip() for line in lines)
		results.append(paragraph)
	return "\n\n".join(results)

class Weather(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.weather_data = WeatherData(**config.weather_data.__dict__)
		self.weather_data.appid == os.path.expandvars(self.weather_data.appid) # Expand environment variables
		self.refresh_minutes = 5
		self.set_timeout(1) # refresh right away
		self.weather_response = None
		self.weather_api = OpenWeatherMap()

	def render(self, force: bool = False) -> int:
		if not self.weather_response: return 0
		gfx = copy.copy(self.gfx)
		degrees = "\u00B0F"  # Degree symbol for Fahrenheit
		x = gfx.x0
		y = gfx.y0
		w = SimpleNamespace(**self.weather_response["current"])
		text = self.screen.text
		text_box = self.screen.text_box
    	# text_box(self, gfx: PMGfx, msg: str, rect: tuple, valign: str = "center", halign: str = "center") -> None:
		# text(gfx, f"Temp: {w.temp}F\nHumidity: {w.humidity}\nFeels Like: {w.feels_like}F\n{w.weather[0].descripition}", x, y)
		text_box(gfx, "Weather", gfx.rect, valign="top")
		y += gfx.font_size / 2  # Offset for the text
		gfx.text_color = self.config.body_color or gfx.text_color
		text_box(gfx, f"{w.temp}{degrees}", (x, y + gfx.font_size, gfx.x1, y + gfx.font_size * 2))
		text_box(gfx, f"{w.humidity} %", (x, y + gfx.font_size * 2, gfx.x1, y + gfx.font_size * 3))
		text_box(gfx, f"{w.feels_like}{degrees}", (x, y + gfx.font_size * 3, gfx.x1, y + gfx.font_size * 4))
		self.weather_response = None  # Clear response after rendering
		return 1

	def exec(self) -> bool:
		if not self.is_timedout(): return False
		self.weather_response = self.weather_api.fetch(self.weather_data)
		# print(json.dumps(self.weather_response, indent=2))
		self.set_timeout(self.refresh_minutes * 60 * 1000)
		if self.weather_response.get("alerts"):
			alerts = self.weather_response["alerts"]
			if alerts:
				alert = alerts[0]
				event = AlertEvent("weather_alert", alert["event"], f"{_paragraph_fix(alert['description'])}", self.refresh_minutes * 60 * 1000)
				self.pm.add_event(event)
		return True

	def onEvent(self, event):
		pass			
			
		
def main():
	parms = WeatherData(37.5037, -77.6428, "appid", "minutely,hourly,daily", "imperial", "english")	
	weather = OpenWeatherMap()
	current = weather.fetch(parms)
	print(json.dumps(current, indent=2))

if __name__ == "__main__":
	main()

