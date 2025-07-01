from pymirror.pmmodule import PMModule

class PymirrorController(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self._pymirror = config.pymirror
		self.subscribe("PyMirrorEvent")

	def render(self):
		return False

	def exec(self):
		return False

	def onEvent(self, event):
		if event.event == "PyMirrorEvent":
			if event.debug != None: self.pm.debug = event.debug
		else:
			print(f"Received unknown event type: {event.type}")

