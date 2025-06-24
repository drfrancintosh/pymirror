import importlib
import json
from pymirror.pmscreen import PMScreen
from pymirror.safe_namespace import SafeNamespace
from pymirror.utils import snake_to_pascal

def _color(arr):
	if arr is None: return None
	if isinstance(arr, str):
		if arr.startswith("#"):
			# Convert hex color to RGB tuple
			arr = arr.lstrip("#")
			if len(arr) == 6:
				return tuple(int(arr[i:i+2], 16) for i in (0, 2, 4))
			elif len(arr) == 8:
				return tuple(int(arr[i:i+2], 16) for i in (0, 2, 4))
			else:
				raise ValueError(F"Invalid hex color format {arr}, expected #RRGGBB or #RRGGBBAA.")
		elif arr.startswith("(") and arr.endswith(")"):
			# Convert rgb() string to RGB tuple
			arr = arr[1:-1].split(',')
			arr = [int(x.strip()) for x in arr]
			if len(arr) < 3 or len(arr) > 4:
				raise ValueError(F"Invalid rgb() format, expected (R, G, B) or (R, G, B, A).")
	if len(arr) == 3:
		return tuple(arr)  # RGB tuple
	elif len(arr) == 4:
		return tuple(arr[:3])  # RGBA tuple, ignore alpha
	else:
		raise ValueError(f"Invalid color format, {arr} expected RGB or RGBA tuple.")

class PyMirror:
	def __init__(self, config_fname):
		with open(config_fname, 'r') as file:
			self.config = SafeNamespace(**json.load(file))
		self.screen = PMScreen()
		self.screen.gfx.color = _color(self.config.color) or (255, 255, 255)  # default color
		self.screen.gfx.bg_color = _color(self.config.bg_color) or (0, 0, 0)
		self.screen.gfx.text_color = _color(self.config.text_color) or _color(self.screen.gfx.color)
		self.screen.gfx.text_bg_color = _color(self.config.text_bg_color)
		self.screen.gfx.line_width = self.config.line_width or 5
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
