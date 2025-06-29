# weather.py
# https://openweathermap.org/api/one-call-3#current

import requests
import copy
import json
from jinja2 import Template

from pymirror import PMCard
from pymirror.utils import expand_dict
from pymirror import PMTimer

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

class WebApi(PMCard):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self._web_api = config.web_api
		self.api = Api(self._web_api)
		self.timer.set_timeout(0.1) # refresh right away
		self.display_timer = PMTimer(0)
		self.response = None
		self.items = []
		self.item_number = 0
		self.update("", "", "")  # Initialize with empty strings

	def _read_items(self, force: bool = False) -> int:
		context = {
			"_n_": 0,
			"payload": self.response,
		}
		self.items = []

		 # extract the maximum number of items to display
		display = copy.copy(self._web_api.display.__dict__)
		expand_dict(display, context)
		max_items = int(display.get("max", "1"))
		total_items = int(display.get("total", "1"))
		if total_items > max_items:
			total_items = max_items
		for n in range(total_items):
			context["_n_"] = n
			display = copy.copy(self._web_api.display.__dict__)
			expand_dict(display, context) # extract the 'nth' item to display
			self.items.append(display)	
		return len(self.items)
	
	def _read_api(self):
		self.response = self.api.fetch()
		if self.response.get("error"):
			print(f"Error fetching data: {self.response['error']}")
			return False
		self._read_items()

	def _display_next_item(self):
		if self.item_number >= len(self.items):
			self.item_number = 0
		self.header = self.items[self.item_number].get("header", "")
		self.body = self.items[self.item_number].get("body", "")
		self.footer = self.items[self.item_number].get("footer", "")
		self.update(self.header, self.body, self.footer)
		self.item_number += 1
	
	def exec(self) -> bool:
		update = super().exec()
		if self.timer.is_timedout():
			self._read_api()
			self.timer.set_timeout(self._web_api.update_mins * 60 * 1000)
			self.display_timer.set_timeout(0.1)
			update = True

		if self.display_timer.is_timedout():
			self._display_next_item()
			self.display_timer.set_timeout(self._web_api.cycle_seconds * 1000)
			update = True

		return update
