import time
from pymirror.pmmodule import PMModule
from pymirror.pmevent import PMEvent
from dataclasses import dataclass

@dataclass
class AlertEvent(PMEvent):
	message: str
	timeout: int

class Alert(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.last_message = None
		self.message = config.welcome_message
		self.set_timeout(config.display_time)
		self.subscribe("ALERT")

	def render(self):
			gfx = self.gfx
			gfx.text_bg_color = gfx.bg_color # Set background color for text
			print(f"Rendering alert: {self.message[:20]}, text_color={gfx.text_color}, bg_color={gfx.bg_color}")
			self.screen.text_box(gfx, self.message or "", gfx.x0, gfx.y0, gfx.x1, gfx.y1, valign="top")
			# self.last_message = self.message
			return 1


	def exec(self):
		# if self.is_timedout(): self.message = None
		# if self.message == self.last_message: return 0
		return self.render()

	def onAlertEvent(self, event):
		print(f"Alert received: {event.message}")
		self.message = event.message
		self.set_timeout(event.timeout)
	
	def onEvent(self, event):
		handlers = {
			"ALERT": self.onAlertEvent,
		}
		handler = handlers.get(event.name)
		if handler: handler(event)
		else: print(f"No handler for {event.name}")

