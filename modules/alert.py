import time
import copy
from pymirror.pmmodule import PMModule
from pymirror.pmevent import PMEvent
from dataclasses import dataclass

@dataclass
class AlertEvent(PMEvent):
	heading: str
	message: str
	timeout: int

class Alert(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.last_message = None
		self.last_heading = None
		self.heading = config.heading.text
		self.message = config.welcome_message
		self.timer.set_timeout(config.display_time)

	def _render_heading(self) -> int: # returns next y position
		gfx = self.gfx
		next_y0 = gfx.y0
		hdg = self.config.heading
		if hdg:
			gfx2 = copy.copy(self.gfx)
			gfx2.set_font(hdg.font or gfx.font_name, hdg.font_size or gfx.font_size)
			gfx2.text_color = hdg.text_color or gfx.text_color
			gfx2.text_bg_color = hdg.text_bg_color or gfx.text_bg_color
			rect = (gfx2.x0, next_y0, gfx2.x1, next_y0 +gfx2.font_size)
			self.screen.text_box(gfx2, self.heading, rect, halign="center", valign="center")
			next_y0 += gfx2.font_size
		return next_y0

	def _render_body(self, y0) -> None:
		gfx = self.gfx
		rect = (gfx.x0, y0, gfx.x1, gfx.y1)
		self.screen.text_box(gfx, self.message or "", rect, halign="left", valign="center")

	def _update_message(self, heading: str, message: str) -> None:
		self.last_message = self.message
		self.last_heading = self.heading
		self.heading = heading
		self.message = message

	def _has_message_changed(self) -> bool:
		return self.message != self.last_message or self.heading != self.last_heading
	
	def render(self, force=False) -> bool:
		update = force or self._has_message_changed()
		if update:
			print(f"Alert module rendering: {self.heading} - {self.message}")
			self.clear_region()
			next_y0 = self._render_heading()
			self._render_body(next_y0)
			self._update_message(self.heading, self.message)
		return update

	def exec(self) -> bool:
		if self.timer.is_timedout(): 
			self._clear_message()
			return True
		return self._has_message_changed()	

	def onEvent(self, event) -> None:
		if isinstance(event, AlertEvent):
			self._update_message(event.heading, event.message)
			self.timer.set_timeout(event.timeout)
		elif isinstance(event, dict):
			self._update_message(event.get("heading", ""), event.get("message", ""))
			self.timer.set_timeout(event.get("timeout", 0))
		else:
			print(f"Alert module received unexpected event: {event.name}")