import time
from pymirror.pmmodule import PMModule

class Cron(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self._pymirror = config.pymirror
		self.subscribe("PyMirrorEvent")

	def render(self):
		return False

	def exec(self):
		return False

	def onEvent(self, event):
		match event.command:
			case "debug":
				self.pm.debug = event.value
				pass
			case "stop":
				print("Stopping PyMirror...")
				pass
			case "pause":
				print("Pausing PyMirror...")
				pass
			case _:
				print(f"Unknown command: {event.command}")
				pass


