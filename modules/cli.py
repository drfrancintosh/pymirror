# weather.py
# https://openweathermap.org/api/one-call-3#current

import copy
import subprocess

from dataclasses import dataclass
from pymirror.pmmodule import PMModule
from modules.alert import AlertEvent
from pymirror.utils import expand_dict, SafeNamespace
from pymirror.pmtimer import PMTimer

class Cli(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.timer.set_timeout(1)  # refresh right away

	def _render_text(self, field, x0, y0, x1, y1, config, halign="center", valign="center") -> int: # returns next y position
		context = {
			"title": self.config.title,
			"stdout": self.stdout,
			"command": self.config.command,
		}
		self.items = []

		 # extract the maximum number of items to display
		display = copy.copy(self.config.display.__dict__)
		expand_dict(display, context)

		gfx = self.gfx
		gfx2 = copy.copy(self.gfx)
		gfx2.set_font(config.font or gfx.font_name, config.font_size or gfx.font_size)
		gfx2.text_color = config.color or gfx.text_color
		gfx2.text_bg_color = config.bg_color or gfx.text_bg_color
		rect = (x0, y0, x1, y1)
		self.screen.text_box(gfx2, display[field], rect, halign=halign, valign=valign)

	def render(self, force: bool = False) -> bool:
		self.clear_region()
		gfx = self.gfx
		self._render_text('header', gfx.x0, gfx.y0, gfx.x1, gfx.y0 + self.config.fonts.header.font_size * 2, self.config.fonts.header, halign="left", valign="top")
		self._render_text('body', gfx.x0, gfx.y0 + self.config.fonts.header.font_size * 2, gfx.x1, gfx.y1, self.config.fonts.body, halign="center", valign="center")
		self._render_text('footer', gfx.x0, gfx.y1 - self.config.fonts.footer.font_size, gfx.x1, gfx.y1, self.config.fonts.footer, halign="center", valign="center")
		self.item_number += 1
		return True
	
	def exec(self) -> bool:
		if self.timer.is_timedout():
			self.stdout = subprocess.check_output(self.config.command, shell=True, text=True)
			self.timer.set_timeout(self.config.cycle_seconds * 1000)
			return True
		return False
	
	def onEvent(self, event):
		pass			
