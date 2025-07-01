from pymirror.pmmodule import PMModule

class PymirrorController(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self._pymirror = config.pymirror
		self.subscribe("PyMirrorEvent")

	def render(self, force: bool = False) -> bool:
		return False

	def exec(self):
		return False

	def onEvent(self, event):
		if event.event != "PyMirrorEvent":
			print(f"Received unknown event type: {event.type}")
			return
		if event.debug == "true" or event.debug == "false": 
			self.pm.debug = event.debug == "true"
			self.pm.full_render()
		if event.refresh != None: 
			self.pm.full_render()
		if event.error != None: 
			raise Exception(f"PyMirrorController received error event:\n{event.error}")

