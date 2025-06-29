# weather.py
# https://openweathermap.org/api/one-call-3#current

import copy
import subprocess

from pymirror.pmmodule import PMModule
from pymirror.utils import expand_dict
from pymirror.pmcard import PMCard

class Cli(PMCard):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self._cli = config.cli
		self.timer.set_timeout(1)  # refresh right away

	def exec(self) -> bool:
		super().exec()
		if self.timer.is_timedout():
			self.stdout = subprocess.check_output(self._cli.command, shell=True, text=True).strip()
			context = {
				"title": self.moddef.name,
				"stdout": self.stdout,
				"command": self._cli.command,
			}
			dict = {
				"header": self._cli.header,
				"body": self._cli.body,
				"footer": self._cli.footer,
			}
			expand_dict(dict, context)
			self._card.header.text = dict.get('header')
			self._card.body.text = dict.get('body')
			self._card.footer.text = dict.get('footer')
			return True
		return False
	
	def onEvent(self, event):
		pass			
