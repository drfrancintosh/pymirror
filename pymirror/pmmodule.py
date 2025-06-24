from abc import ABC, abstractmethod
import time
from pymirror.pmscreen import PMGfx

class PMModule(ABC):
	def __init__(self, pm, moddef, config):
		## Initialize the module based on moddef
		## NOTE: config is often moddef.config, but not always
		## NOTE: we only init the module on moddef, not on config
		##	   this is because moddef is the generic module definition, 
		##     and config is the module "child" instance configuration
		self.pm = pm
		self.screen = pm.screen
		self.moddef = moddef
		self.config = config
		self.timeout = 0
		self.subscriptions = []
		self.position = moddef.position
		self.x_offset = moddef.x_offset or 0
		self.y_offset = moddef.y_offset or 0
		self.gfx = PMGfx() ## default graphics context
		self.gfx.font_name = moddef.font or "DejaVuSans.ttf"
		self.gfx.font_size = moddef.font_size or 64
		self.gfx.set_font(self.gfx.font_name, self.gfx.font_size)
		if self.moddef.position:
			dims = pm.config.positions[self.moddef.position]
			## this is the bounding box for the module
			## x0, y0 is the top-left corner, x1, y1 is the bottom-right corner
			## these are in percentages of the screen size
			## so we need to multiply by the screen size to get the actual pixel values
			## NOTE: self.x_offset and self.y_offset are used by the render() method
			## 		 to offset the text position within the bounding box
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
