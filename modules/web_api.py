# weather.py
# https://openweathermap.org/api/one-call-3#current

import os
import requests
import json
import copy
from jinja2 import Template

from dataclasses import dataclass
from pymirror.pmmodule import PMModule
from modules.alert import AlertEvent
from pymirror.utils import expand_dict, SafeNamespace
from pymirror.pmtimer import PMTimer

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
		self.timer.set_timeout(1) # refresh right away
		self.display_timer = PMTimer(0)
		self.response = None
		self.item_number = 0
		self.max_items = 1

	def _render_body(self, y0, msg) -> None:
		gfx = self.gfx
		rect = (gfx.x0, y0, gfx.x1, gfx.y1)
		self.screen.text_box(gfx, msg or "<empty>", rect, halign="left", valign="center")

	def render(self, force: bool = False) -> int:
		context = {
			"_n_": 0,
			"payload": self.response,
		}

		 # extract the maximum number of items to display
		display = copy.copy(self.config.display.__dict__)
		expand_dict(display, context)
		self.max_items = int(display.get("max", "1"))
	
		# reset the item number if necessar
		if self.item_number >= self.max_items:
			self.item_number = 0

		# extract the 'nth' item to display
		context["_n_"] = self.item_number
		display = copy.copy(self.config.display.__dict__)
		expand_dict(display, context) # extract the 'nth' item to display
		print(f"WebApi.render: {self.item_number} {display}, context: {context}")
		self._render_body(self.gfx.y0, display['header'])
		self.item_number += 1

		return 0

	def exec(self) -> bool:
		if self.timer.is_timedout():
			self.response = self.api.fetch()
			self.timer.set_timeout(self.config.update_mins * 60 * 1000)
			self.display_timer.set_timeout(1)
			self.item_number = 0
			self.max_items = 1
			if self.response.get("error"):
				print(f"Error fetching data: {self.response['error']}")
		if self.display_timer.is_timedout():
			self.display_timer.set_timeout(self.config.cycle_seconds * 1000)
			if self.response:
				self.render()
				return True
		return False
	
	def onEvent(self, event):
		pass			
