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
		self.message = config.welcome_message
		self.set_timeout(config.display_time)

	def _render_heading(self) -> int: # returns next y position
		next_y0 = gfx.y0
		hdg = self.config.heading
		if hdg:
			gfx = self.gfx
			gfx2 = copy.copy(self.gfx)
			gfx2.set_font(hdg.font or gfx.font_name, hdg.font_size or gfx.font_size)
			gfx2.text_color = hdg.text_color or gfx.text_color
			gfx2.text_bg_color = hdg.text_bg_color or gfx.text_bg_color
			self.screen.text_box(gfx2, self.header, gfx2.x0, next_y0, gfx2.x1, gfx2.y1 + gfx2.font_size, halign="center", valign="top")
			next_y0 += gfx2.font_size
		return next_y0

	def _render_body(self, y0) -> None:
			gfx = self.gfx
			self.screen.text_box(gfx, self.message, gfx.x0, y0, gfx.x1, gfx.y1, halign="left", valign="top")

	def render(self, force=False) -> bool:
			update = force or self.message != self.last_message
			if update:
				self.clear_region()
				next_y0 = self._render_heading()
				self._render_body(next_y0)
				self.last_message = self.message
			return update

	def exec(self) -> bool:
		if self.is_timedout(): self.message = None ## clear message
		if self.message == self.last_message: return False
		else: return True

	def onAlertEvent(self, event) -> None:
		self.heading = event.heading
		self.message = event.message
		self.set_timeout(event.timeout)
	
	def onEvent(self, event) -> None:
		handlers = {
			"ALERT": self.onAlertEvent,
		}
		handler = handlers.get(event.name)
		if handler: handler(event)
		else: print(f"No handler for {event.name}")

