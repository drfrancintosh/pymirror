import time
from pymirror.pmmodule import PMModule

class Alert(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self.message = config.welcome_message
		self.set_timeout(config.display_time)
		self.config = config
		self.subscribe("ALERT")
		self.gfx.set_font("", 64)

	def render(self):
		if self.message:
			gfx = self.gfx
			self.screen.text_box(gfx, self.message, gfx.x0, gfx.y0, gfx.x1, gfx.y1)

	def exec(self):
		if self.is_timedout():
			self.message = None
		else:
			self.render()

	def onAlertEvent(self, event):
		self.message = event.message
		self.set_timeout(event.timeout)
	
	def onEvent(self, event):
		handlers = {
			"ALERT": self.onAlertEvent,
		}
		handler = handlers.get(event.name)
		if handler: handler(event)
		else: print(f"No handler for {event.name}")

