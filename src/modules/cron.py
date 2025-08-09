from pymirror.pmmodule import PMModule
from pymirror.pmlogger import _debug

class CronModule(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self._cron = config.cron
		self.name = self._cron.name
		self.event = self._cron.event
		self.repeat = self._cron.repeat ## number of times to repeat, -1 = forever
		self.delay = self._cron.delay
		if self._cron.first_delay: self.timer.set_timeout(self._cron.first_delay) ## emit event immediately
		else: self.timer.set_timeout(self.delay)

	def render(self, force: bool = False) -> bool:
		pass

	def exec(self):
		if self.timer.is_timedout():
			_debug(f"CronModule: Executing {self.name} event {self.event} with repeat {self.repeat} and delay {self.delay}")
			if self.repeat == 0: return 0
			self.publish_event(self.event)
			if self.repeat > 0: self.repeat -= 1
			self.timer.set_timeout(self.delay) # note: self.repeat < 0 repeats forever
		return 0

	def onEvent(self, event):
		pass
	

