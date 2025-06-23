import time
from pymirror.pmmodule import PMModule

class Cron(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.name = config.name
		self.event = config.event
		self.repeat = config.repeat ## number of times to repeat, -1 = forever
		self.delay = config.delay
		if config.first_delay: self.set_timeout(config.first_delay) ## emit event immediately
		else: self.set_timeout(self.delay)

	def render(self):
		pass

	def exec(self):
		if self.is_timedout():
			if self.repeat == 0: return
			self.pm.add_event(self.event)
			if self.repeat > 0: self.repeat -= 1
			self.set_timeout(self.delay) # note: self.repeat < 0 repeats forever

	def onEvent(self, event):
		pass
	

