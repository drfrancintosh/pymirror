from abc import ABC, abstractmethod
import time
from pymirror.pmscreen import PMGfx

class PMModule(ABC):
	def __init__(self, pm, config):
		self.pm = pm
		self.screen = pm.screen
		self.pygame = pm.pygame
		self.config = config
		self.timeout = 0
		self.subscriptions = []
		self.position = config.position
		self.gfx = PMGfx()
		self.gfx.x0 = 0
		self.gfx.y0 = 0
		self.gfx.x1 = self.pm.screen.gfx.width / 3
		self.gfx.y1 = self.pm.screen.gfx.height / 3


	def subscribe(self, name):
		self.subscriptions.append(name)

	def is_subscribed(self, name):
		return name in self.subscriptions

	def set_timeout(self, ms):
		if not ms: ms = ms
		else: self.timeout = time.time() + ms / 1000

	def is_timedout(self):
		if not self.timeout: return True # disabled timer always returns timedout==true
		if time.time() < self.timeout:
			return False ## we're not timed out yet
		else:
			self.set_timeout(0) ## disable timer
			return True

	@abstractmethod
	def render(self):
		pass

	@abstractmethod
	def exec(self):
		pass

	@abstractmethod
	def onEvent(self, event):
		pass
