import importlib
import json
import copy
import os
from pymirror.pmscreen import PMScreen
from pymirror.safe_namespace import SafeNamespace
from pymirror.utils import snake_to_pascal
from dotenv import load_dotenv

class PyMirror:
	def __init__(self, config_fname):
		# Load environment variables from .env file
		load_dotenv()  
		with open(config_fname, 'r') as file:
			self.config = SafeNamespace(**json.load(file))
		self.config.secrets
		# Load secrets from .secrets file if specified
		load_dotenv(dotenv_path=os.path.expandvars(self.config.secrets) if self.config.secrets else ".secrets")
		self.screen = PMScreen(self.config.screen)

		self.screen.set_flush(False)
		self.modules = []
		self.new_events = []
		self.events = []

		self._load_modules()

	def _load_modules(self):
		for module_config in self.config.modules:
			## load the module dynamically
			if type(module_config) is str:
				## if moddef is a string, it is the name of a module config file
				## load the module definition from the file
				## the file should be in JSON format
				with open(module_config, 'r') as file:
					module_config = SafeNamespace(**json.load(file))
			## import the module using its name
			## all modules should be in the "modules" directory
			mod = importlib.import_module("modules."+module_config.module)
		
			## get the class from inside the module
			## convert the file name to class name inside the module
			## by convention the filename is snake_case and the class name is PascalCase
			clazz_name = snake_to_pascal(module_config.module)
			clazz = getattr(mod, clazz_name)

			## create an instance of the class (module)
			## and pass the PyMirror instance and the module config to it
			## See pymirror.PMMModule for the expected constructor
			obj = clazz(self, module_config.moddef, module_config.config)

			## add the module to the list of modules
			self.modules.append(obj)

	def _send_events(self, module):
		for event in self.events:
			if module.is_subscribed(event.name):
				module.onEvent(event)

	def add_event(self, event):
		self.new_events.append(event)

	def _debug(self, module):
		gfx = copy.copy(self.screen.gfx)
		self.screen.rect(gfx, module.gfx.rect, fill=None)
		gfx.set_font(gfx.font_name, 24)
		self.screen.text(gfx, f"{module.moddef.name}", module.gfx.x0 + gfx.line_width, module.gfx.y0 + gfx.line_width)

	def full_render(self):
		self.screen.clear()
		for module in self.modules:
			if module.moddef.disabled: continue
			module.render(self.screen, force=True)
			if self.config.debug: self._debug(module)

	def run(self):
		self.screen.clear()
		while True:
			self.events = self.new_events # dispose of old events, process new events
			self.new_events = []
			is_dirty = 1
			for module in self.modules:
				if module.moddef.disabled: continue
				self._send_events(module)
				do_update = module.exec() # exec() returns 1 render update is needed
				if do_update:
					is_dirty += module.render(force=False) # render() returns 1 if something changed
				if self.config.debug: self._debug(module)
			if is_dirty:
				self.screen.flush()

def main():
	pm = PyMirror("config.json")
	pm.run()

if __name__ == "__main__":
	main()
