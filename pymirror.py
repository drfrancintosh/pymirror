import importlib
import time
import json
from types import SimpleNamespace
from pymirror.pmscreen import PMScreen

class SafeNamespace(SimpleNamespace):
    def __getattr__(self, name):
        return None

def _snake_to_pascal(snake_str):
    return ''.join(word.capitalize() for word in snake_str.split('_'))
def _recursive_namespace(d):
    if isinstance(d, dict):
        return SafeNamespace(**{k: _recursive_namespace(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [_recursive_namespace(i) for i in d]
    else:
        return d

class PyMirror:
	def __init__(self, config_fname):
		with open(config_fname, 'r') as file:
			self.config = _recursive_namespace(json.load(file))
		self.screen = PMScreen()
		self.pygame = self.screen.pygame
		self.screen.set_flush(False)
		self.modules = []
		self.new_events = []
		self.events = []
		self._load_modules()

	def _load_modules(self):
		for module in self.config.modules:
			mod = importlib.import_module("modules."+module.module)
			clazz_name = _snake_to_pascal(module.module)
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
