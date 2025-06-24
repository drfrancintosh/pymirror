import time
from pymirror.pmmodule import PMModule

class Alert(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.last_message = None
		self.message = config.welcome_message
		self.set_timeout(config.display_time)
		self.subscribe("ALERT")

	def render(self):
		if self.message != self.last_message:
			gfx = self.gfx
			self.screen.text_box(gfx, self.message, gfx.x0, gfx.y0, gfx.x1, gfx.y1)
			self.last_message = self.message


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

