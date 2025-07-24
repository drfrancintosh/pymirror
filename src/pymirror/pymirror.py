import importlib
import json
import copy
import os
import sys
import time
from dotenv import load_dotenv
import queue
import argparse
import traceback

from pymirror.pmscreen import PMScreen
from pymirror.utils import snake_to_pascal, expand_dict, SafeNamespace
from pmserver.pmserver import PMServer
from events import * # get all events 

def _to_null(s):
    """ Convert a string to None if it is 'null' or 'None' """
    if s in ["null", "None"]:
        return None
    return s

class PyMirror:
    def __init__(self, config_fname, args):
        ## by convention, all objects get a copy of the config
        ## so that they can access it without having to pass it around
        ## and they "pluck out" the values they need
        print(f"args: {args}")
        self._config = self._load_config(config_fname)
        if args.output_file:
            self._config.screen.output_file = _to_null(args.output_file)
        if args.frame_buffer:
            self._config.screen.frame_buffer = _to_null(args.frame_buffer)
        print(f"Using config: {self._config}")
        self.screen = PMScreen(self._config)
        self.force_render = False
        self.debug = self._config.debug
        self.modules = []
        self.events = []
        self.server_queue = queue.Queue()  # Use a queue to manage events
        self.server = PMServer(self._config.server, self.server_queue)
        self._clear_screen = True  # Flag to clear the screen on each loop
        self._clear_screen_again = False  # Flag to reset the screen on each loop
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
                    try:
                        config = json.load(file)
                        expand_dict(config, {})  # Expand environment variables in the config
                        module_config = SafeNamespace(**config)
                    except Exception as e:
                        print(f"Error loading module config from {module_config}: {e}")
                        sys.exit(1)
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
            while event := self.server_queue.get(0):
                print(f"Received event from server: {event}")
                self.publish_event(event)
        except queue.Empty:
            # No new events in the queue
            pass


    def _send_events_to_module(self, module, events):
        if not module.subscriptions: return
        for event in events:
            if event.event in module.subscriptions:
                print(f"... Event {event.event} to module {module._moddef.name}")
                module.onEvent(event)

    def _convert_events_to_namespace(self):
        """ Convert a list of events to SafeNamespace objects """
        return [SafeNamespace(event) if isinstance(event, dict) else event for event in self.events]

    def _send_all_events(self):
        if not self.events: return
        self.events = self._convert_events_to_namespace()  # Convert events to SafeNamespace if needed
        for module in self.modules:
            if not module.subscriptions: continue
            self._send_events_to_module(module, self.events)  # Send all events to the module
        self.events.clear()  # Clear the events after sending them

    def publish_event(self, event: dict):
        if type(event) is dict:
            self.events.append(SafeNamespace(**event))
        elif isinstance(event, SafeNamespace):
            self.events.append(event)
        else:
            raise TypeError(f"Event must be a dict or SafeNamespace, got {type(event)}")
    
    def _debug(self, module):
        scrn_gfx = copy.copy(self.screen.gfx)
        if not module.gfx.rect: return
        self.screen.bitmap.rect(scrn_gfx, module.gfx.rect, fill=None)
        scrn_gfx.set_font(scrn_gfx.font_name, 24)
        module._time = module._time if hasattr(module, '_time') else 0.0
        self.screen.bitmap.text(scrn_gfx, f"{module._moddef.name} ({module._time:.2f}s)", module.gfx.x0 + scrn_gfx.line_width, module.gfx.y0 + scrn_gfx.line_width)
        self.screen.bitmap.text_box(scrn_gfx, f"{module._moddef.position}", module.gfx.rect, halign="right", valign="top")

    def full_render(self):
        self.screen.bitmap.clear()
        for module in self.modules:
            if module.disabled: continue
            if not module.bitmap: continue
            module.render(force=True)
            self.screen.bitmap.paste(module.gfx, module.bitmap)
        if self.debug: self._debug(module)
        self.screen.flush()  # Flush the screen to show all modules at once

    def _exec_modules(self):
        modules_changed = []
        for module in self.modules:
            module._time = 0.0  # Reset the time for each module
            if not module.disabled:
                start_time = time.time()  # Start timing the module execution
                state_changed = module.exec() # update module state (returns True if the state has changed)
                if state_changed: modules_changed.append(module)
                end_time = time.time()  # End timing the module execution
                module._time = end_time - start_time  # Calculate the time taken for module execution
        return modules_changed

    def _render_modules(self, modules_changed):
        """ Render all modules that have changed state """
        for module in modules_changed:
            if not module.disabled and module.bitmap:
                start_time = time.time()  # Start timing the module rendering
                module.render(force=self.force_render)
                end_time = time.time()  # End timing the module rendering
                module._time += end_time - start_time  # add on the time taken for module rendering

    def _update_screen(self):
        self.screen.bitmap.clear()  # Clear the bitmap before rendering
        for module in reversed(self.modules):
            if not module.disabled and module.bitmap:
                self.screen.bitmap.paste(module.gfx, module.bitmap)
                if self.debug: self._debug(module) # draw boxes around each module if debug is enabled
        self.screen.flush()

    def run(self):
        try:
            while True:
                self._read_server_queue() # read any new events from the server queue
                self._send_all_events()  # send all new events to the modules
                modules_changed = self._exec_modules() # update / check the state of all modules
                self._render_modules(modules_changed)  # Render only the modules that changed state
                self._update_screen()  # Update the screen with the rendered modules
                time.sleep(0.01) # Sleep for a short time to give pmserver a chance to process web requests
        except Exception as e:
            traceback.print_exc()  # <-- This prints the full stack trace to stdout
            self._error_screen(e)  # Display the error on the screen

    def _error_screen(self, e):
        """ Display an error screen with the exception details """
        self.screen.bitmap.clear()
        self.screen.gfx.text_color = "#f00"
        self.screen.gfx.text_bg_color = "#ff0"
        self.screen.bitmap.text_box(self.screen.gfx, f"Exception:\n\n{str(e)}", (0, 0, self.screen.gfx.width, self.screen.gfx.height), valign="center", halign="center")
        self.screen.flush()

    def _bsod(self, e):
        """ Blue Screen of Death """
        tb_lines = traceback.format_exception(type(e), e, e.__traceback__)
        error_lines = [line.split("\n")[0] for line in tb_lines if line.lstrip().startswith("File ")]
        error_lines = "\n".join(error_lines)
        error_lines = str(e) + "\n\n" + error_lines
        self.screen.bitmap.clear()
        self.screen.gfx.text_color = "#ccc"
        self.screen.gfx.text_bg_color = "#00f"
        self.screen.gfx.font_name = "DejaVuSerif"
        self.screen.gfx.set_font(self.screen.gfx.font_name, 32)
        self.screen.bitmap.text_box(self.screen.gfx, f"Exception: {error_lines}", (0, 0, self.screen.gfx.width, self.screen.gfx.height), valign="center", halign="left")
        self.screen.flush()



def main():
    parser = argparse.ArgumentParser(description="PyMirror Smart Mirror Application")
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Path to config JSON file (default: config.json)"
    )
    parser.add_argument(
        "--frame_buffer",
        metavar="DEVICE",
        help="Frame buffer device path (e.g., /dev/fb0, /dev/fb1)"
    )
    parser.add_argument(
        "--output_file",
        metavar="PATH",
        help="Output file path for screen capture (supports .jpg, .png formats). "
            "Overrides the output_file setting in config."
    )
    args = parser.parse_args()
    args = parser.parse_args()

    pm = PyMirror(args.config, SafeNamespace(**vars(args)))
    pm.run()

if __name__ == "__main__":
    main()
