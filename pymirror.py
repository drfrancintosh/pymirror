import importlib
import json
from pymirror.pmscreen import PMScreen
from pymirror.safe_namespace import SafeNamespace
from pymirror.utils import snake_to_pascal

class PyMirror:
	def __init__(self, config_fname):
		with open(config_fname, 'r') as file:
			self.config = SafeNamespace(**json.load(file))
		self.screen = PMScreen()
		self.screen.set_flush(False)
		self.modules = []
		self.new_events = []
		self.events = []
		self._load_modules()

	def _load_modules(self):
		for module in self.config.modules:
			mod = importlib.import_module("modules."+module.module)
			clazz_name = snake_to_pascal(module.module)
			clazz = getattr(mod, clazz_name)
			obj = clazz(self, module.config)
			self.modules.append(obj)

	def add_event(self, event):
		self.new_events.append(event)

	def send_events(self, module):
		for event in self.events:
			if module.is_subscribed(event.name):
				module.onEvent(event)

	def run(self):
		while True:
			self.screen.clear()
			self.events = self.new_events # dispose of old events, process new events
			self.new_events = []
			for module in self.modules:
				self.send_events(module)
				module.exec()
			self.screen.flush()

def main():
	pm = PyMirror("config.json")
	pm.run()

if __name__ == "__main__":
	main()
