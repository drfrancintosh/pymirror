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
		is_dirty = super().exec()
		if self.timer.is_timedout():
			print(f"Executing CLI command: {self._cli.command}")
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
			self._card.header.text = dict.get('header') if self._card.header else None
			self._card.body.text = dict.get('body') if self._card.body else None
			self._card.footer.text = dict.get('footer') if self._card.footer else None
			is_dirty = True
		return is_dirty

	def onEvent(self, event):
		pass			
