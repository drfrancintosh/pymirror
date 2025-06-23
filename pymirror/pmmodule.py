from abc import ABC, abstractmethod
import time
from pymirror.pmscreen import PMGfx

class PMModule(ABC):
	def __init__(self, pm, moddef, config):
		self.pm = pm
		self.screen = pm.screen
		self.moddef = moddef
		self.config = config
		print(moddef.__dict__)
		self.timeout = 0
		self.subscriptions = []
		self.position = moddef.position
		self.x_offset = moddef.x_offset or 0
		self.y_offset = moddef.y_offset or 0
		self.gfx = PMGfx() ## default graphics context
		self.gfx.font_name = moddef.font
		self.gfx.font_size = moddef.font_size
		if moddef.font:
			self.gfx.set_font(moddef.font, moddef.font_size)
		if self.moddef.position:
			print(f"Module {self.moddef.module} position: {self.moddef.position}")
			dims = pm.config.positions[self.moddef.position]
			print(f"Module {self.moddef.module} dimensions: {dims}")
			self.gfx.x0 = self.pm.screen.gfx.width * dims[0]
			self.gfx.y0 = self.pm.screen.gfx.height * dims[1]
			self.gfx.x1 = self.pm.screen.gfx.width * dims[2] 
			self.gfx.y1 = self.pm.screen.gfx.height * dims[3] 


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
