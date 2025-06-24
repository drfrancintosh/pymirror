from datetime import datetime
from pymirror.pmmodule import PMModule

class Fps(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.last_time = datetime.now()

	def render(self):
		pass

	def exec(self):
		self.gfx.text_bg_color = (192, 192, 192)  # Set background color for text
		self.gfx.font_size = 32
		self.gfx.reset_font()
		now = datetime.now()
		delta = now - self.last_time
		self.last_time = now
		fps = 1 / delta.total_seconds() if delta.total_seconds() > 0 else 0
		text = self.screen.text
		text(self.gfx, f"FPS: {fps:.2f}", self.gfx.x0, self.gfx.y0)

	def onEvent(self, event):
		pass			

