from datetime import datetime
from pymirror.pmmodule import PMModule

class Fps(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self.last_time = datetime.now()


	def render(self):
		pass

	def exec(self):
		now = datetime.now()
		delta = now - self.last_time
		self.last_time = now
		fps = 1 / delta.total_seconds() if delta.total_seconds() > 0 else 0
		self.gfx.text(f"FPS: {fps:.2f}", self.gfx.x0, self.gfx.y0, self.gfx.font_size)
		
	def onEvent(self, event):
		pass			

