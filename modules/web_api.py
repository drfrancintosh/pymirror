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
		self.items = 0

	def _read_items(self, force: bool = False) -> int:
		context = {
			"_n_": 0,
			"payload": self.response,
		}
		self.items = []

		 # extract the maximum number of items to display
		display = copy.copy(self.config.display.__dict__)
		expand_dict(display, context)
		max_items = int(display.get("max", "1"))
		total_items = int(display.get("total", "1"))
		if total_items > max_items:
			total_items = max_items
		for n in range(total_items):
			context["_n_"] = n
			display = copy.copy(self.config.display.__dict__)
			expand_dict(display, context) # extract the 'nth' item to display
			print(f"WebApi.render: {n} {display}, context: {context}")
			self.items.append(display)	
		return len(self.items)

	def _render_text(self, msg, x0, y0, x1, y1, y_multiplier, config, halign="center", valign="center") -> int: # returns next y position
		gfx = self.gfx
		gfx2 = copy.copy(self.gfx)
		gfx2.set_font(config.font or gfx.font_name, config.font_size or gfx.font_size)
		gfx2.text_color = config.color or gfx.text_color
		gfx2.text_bg_color = config.bg_color or gfx.text_bg_color
		rect = (x0, y0, x1, y1 + gfx2.font_height * y_multiplier)
		self.screen.text_box(gfx2, msg, rect, halign="center", valign="center")
		return y0 + gfx2.font_height * y_multiplier

	def render(self, force: bool = False) -> bool:
		if not force and not self.display_timer.is_timedout(): return False
		self.clear_region()
		gfx = self.gfx
		next_y0 = self._render_text(self.items[0].header, gfx.x0, gfx.y0, gfx.x1, gfx.y0, 1, self.config.fonts.header, halign="center", valign="top")
		self._render_text(self.items[0].body, gfx.x0, next_y0, gfx.x1, gfx.y1, 0, self.config.fonts.body, halign="left", valign="top")
		self._render_text(self.items[0].footer, gfx.x0, gfx.y1, gfx.x1, gfx.y1, -1, self.config.fonts.footer, halign="right", valign="bottom")

	def exec(self) -> bool:
		if self.timer.is_timedout():
			self.response = self.api.fetch()
			if self.response.get("error"):
				print(f"Error fetching data: {self.response['error']}")
				return False
			self.timer.set_timeout(self.config.update_mins * 60 * 1000)
			self.display_timer.set_timeout(1)
			self._read_items()
		return True
	
	def onEvent(self, event):
		pass			
