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
		for moddef in self.config.modules:
			## load the module dynamically
			mod = importlib.import_module("modules."+moddef.module)
			## get the class from inside the module
			## convert the file name to class name inside the module
			## by convention the filename is snake_case and the class name is PascalCase
			clazz_name = snake_to_pascal(moddef.module)
			clazz = getattr(mod, clazz_name)
			## create an instance of the class (module)
			## and pass the PyMirror instance and the module config to it
			## See pymirror.PMMModule for the expected constructor
			obj = clazz(self, moddef, moddef.config)
			## add the module to the list of modules
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
