import time
from pymirror.pmmodule import PMModule

class Alert(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self.message = config.welcome_message
		self.set_timeout(config.display_time)
		self.config = config
		self.subscribe("ALERT")

	def render(self):
		if self.message:
			self.screen.text_box(self.gfx, self.message, 0, 0, -1, -1)

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

