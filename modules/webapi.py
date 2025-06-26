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
from pymirror.utils import expand_dict

class Api:
	def __init__(self, config):
		self.config = config

	def fetch(self):

		response = requests.get(self.config.url, params=self.config.params.__dict__)
		if response.ok:
			return response.json()
		else:
			print(f"Error fetching weather data: {response.status_code} - {response.text}")
			return {"error": "error"}

def _paragraph_fix(text: str) -> str:
	results = []
	paragraphs = text.split("\n\n")
	for paragraph in paragraphs:
		lines = paragraph.split("\n")
		paragraph = " ".join(line.strip() for line in lines)
		results.append(paragraph)
	return "\n\n".join(results)

class WebApi(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.api = Api(config)
		self.set_timeout(1) # refresh right away

	def render(self, force: bool = False) -> int:
		context = {
			"_n_": 0,
			"payload": self.response,
		}
		display = copy.copy(self.config.display.__dict__)
		display = expand_dict(self.response, context)
		print(f"WebApi.render: {display}")

	def exec(self) -> bool:
		if not self.is_timedout(): return False
		self.response = self.api.fetch()
		self.set_timeout(self.config.update_mins * 60 * 1000)
		if self.response.get("error"):
			print(f"Error fetching data: {self.response['error']}")
			return False
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

