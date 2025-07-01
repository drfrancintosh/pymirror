import importlib
import json
import copy
import os
from dotenv import load_dotenv
import queue
import argparse

from pymirror.pmscreen import PMScreen
from pymirror.utils import snake_to_pascal, expand_dict, SafeNamespace
from pmserver.pmserver import PMServer
from events import * # get all events 

class PyMirror:
	def __init__(self, config_fname):
		## by convention, all objects get a copy of the config
		## so that they can access it without having to pass it around
		## and they "pluck out" the values they need
		self._config = self._load_config(config_fname)
		self.screen = PMScreen(self._config)
		self.force_flush = self._config.flush
		self.debug = self._config.debug
		self.modules = []
		self.new_events = []
		self.event_queue = queue.Queue()  # Use a queue to manage events
		self.server = PMServer(self._config.server, self.event_queue)

		self._load_modules()
		self.server.start()  # Start the server to handle incoming events

	def _load_config(self, config_fname) -> SafeNamespace:
		# read .env file if it exists
		load_dotenv()
		# Load the main configuration file
		with open(config_fname, 'r') as file:
			# self.config = SafeNamespace(**json.load(file))
			config = json.load(file)
		# Load secrets from .secrets file if specified
		secrets_path = config.get("secrets")
		if secrets_path:
			secrets_path = os.path.expandvars(secrets_path)
		else:
			secrets_path = ".secrets"
		load_dotenv(dotenv_path=secrets_path)
		# Expand environment variables in the config
		expand_dict(config, os.environ)
		return SafeNamespace(**config)

	def _load_modules(self):
		for module_config in self._config.modules:
			## load the module dynamically
			if type(module_config) is str:
				## if moddef is a string, it is the name of a module config file
				## load the module definition from the file
				## the file should be in JSON format
				with open(module_config, 'r') as file:
					config = json.load(file)
					expand_dict(config, {})  # Expand environment variables in the config
					module_config = SafeNamespace(**config)
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
			obj = clazz(self, module_config)

			## add the module to the list of modules
			self.modules.append(obj)

	def _read_server_queue(self):
		## add any messages that have come from the web server
		try:
			while event := self.event_queue.get(0):
				self.add_event(event)
		except queue.Empty:
			# No new events in the queue
			pass

	def _send_events(self, module, events):
		## send all events to the module
		if not module.subscriptions: return
		for event in events:
			event_name = event.get("event")
			# event_class = None
			# if event_name in module.subscriptions:
			# 	event_class = globals().get(event_name)
			# if event_class:
			# 	event_instance = event_class(**event) if isinstance(event, dict) else SafeNamespace(event)
			# 	module.onEvent(event_instance)
			# else:
			# 	print(f"Unknown event class: {event_name}")
			if event_name in module.subscriptions:
				event = SafeNamespace(**event) if isinstance(event, dict) else event
				module.onEvent(event)

	def add_event(self, event):
		self.new_events.append(event)

	def _debug(self, module):
		scrn_gfx = copy.copy(self.screen.gfx)
		if not module.gfx.rect: return
		self.screen.bitmap.rect(scrn_gfx, module.gfx.rect, fill=None)
		scrn_gfx.set_font(scrn_gfx.font_name, 24)
		self.screen.bitmap.text(scrn_gfx, f"{module._moddef.name}", module.gfx.x0 + scrn_gfx.line_width, module.gfx.y0 + scrn_gfx.line_width)
		self.screen.bitmap.text_box(scrn_gfx, f"{module._moddef.position}", module.gfx.rect, halign="right", valign="top")

	def full_render(self, force=False):
		self.screen.bitmap.clear()
		for module in self.modules:
			if module.disabled: continue
			module.render(force=True)
			if self._config.debug: self._debug(module)

	def run(self):
		self.screen.bitmap.clear()
		while True:
			self._read_server_queue() # read any new events from the server queue
			events = self.new_events # get any new events from server or modules
			self.new_events = [] # displose of the old events
			is_dirty = 0
			for module in self.modules:
				self._send_events(module, events) # send all subscribed events to the module
				if module.disabled: continue
				do_update = module.exec() # update module state (returns True if the state has changed)
				if do_update:
					module_dirty = module.render(self.force_flush) # render() returns True if new rendering occurred
					if module_dirty:
						# Blit the module's image to the screen at the module's position
						self.screen.bitmap.paste(module.gfx, module.bitmap)
						is_dirty += 1
				if self.debug: self._debug(module) # draw boxes around each module if debug is enabled
			if is_dirty:
				# if any new rendering occurred, flush the screen
				# otherwise, the screen will not be updated
				# (this is to improve performance)
				self.screen.flush()

def main():
    parser = argparse.ArgumentParser(description="PyMirror")
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Path to config JSON file (default: config.json)"
    )
    args = parser.parse_args()
    pm = PyMirror(args.config)
    pm.run()

if __name__ == "__main__":
	main()
