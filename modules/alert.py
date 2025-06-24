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
		self.heading = "ALERT"
		self.message = config.welcome_message
		self.set_timeout(config.display_time)
		self.subscribe("ALERT")

	def render(self):
			gfx2 = copy.copy(self.gfx)
			gfx2.font_size = int(self.gfx.font_size * 1.25)
			gfx2.reset_font()
			print(f"gfx2.text_bg_color: {gfx2.text_bg_color}, gfx2.bg_color: {gfx2.bg_color}")
			gfx2.text_bg_color = (255,0,0)
			self.screen.text_box(gfx2, self.heading, gfx2.x0, gfx2.y0, gfx2.x1, gfx2.y0, halign="center", valign="top")
			gfx = self.gfx
			self.screen.text_box(gfx, self.message, gfx.x0, gfx.y0 + gfx2.font_size, gfx.x1, gfx.y1, halign="left", valign="top")
			self.last_message = self.message
			return 1


	def exec(self):
		if self.is_timedout(): self.message = None
		if self.message == self.last_message: return 0
		return self.render()

	def onAlertEvent(self, event):
		print(f"Alert received: {event.message}")
		self.heading = event.heading
		self.message = event.message
		self.set_timeout(event.timeout)
	
	def onEvent(self, event):
		handlers = {
			"ALERT": self.onAlertEvent,
		}
		handler = handlers.get(event.name)
		if handler: handler(event)
		else: print(f"No handler for {event.name}")

