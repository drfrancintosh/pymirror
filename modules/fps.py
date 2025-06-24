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
		now = datetime.now()
		delta = now - self.last_time
		self.last_time = now
		fps = 1 / delta.total_seconds() if delta.total_seconds() > 0 else 0
		text_box = self.screen.text_box
		text_box(self.gfx, f"FPS: {fps:.2f}", self.gfx.x0, self.gfx.y0, self.gfx.x1, self.gfx.y1, "bottom", "right")
		# self.screen.rect(self.gfx, self.gfx.x0, self.gfx.y0, self.gfx.x1, self.gfx.y1, fill=False)

	def onEvent(self, event):
		pass			

