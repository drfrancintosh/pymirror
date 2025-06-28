# weather.py
# https://openweathermap.org/api/one-call-3#current

import copy
import subprocess

from pymirror.pmmodule import PMModule
from pymirror.utils import expand_dict
from pymirror.pmcard import PMCard

class Cli(PMCard):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.timer.set_timeout(1)  # refresh right away

	def exec(self) -> bool:
		if self.timer.is_timedout():
			self.stdout = subprocess.check_output(self.config.command, shell=True, text=True).strip()
			print(f"CLI command '{self.config.command}' executed, output: {self.stdout}")
			context = {
				"title": self.moddef.name,
				"stdout": self.stdout,
				"command": self.config.command,
			}
			print(f"CLI context: {context}")
			dict = {
				"header": self.config.header,
				"body": self.config.body,
				"footer": self.config.footer,
			}
			print(f"CLI dict before expansion: {dict}")
			expand_dict(dict, context)
			print(f"CLI dict after expansion: {dict}")
			self.header = dict.get('header')
			self.body = dict.get('body')
			self.footer = dict.get('footer')
			return True
		return False
	
	def onEvent(self, event):
		pass			
