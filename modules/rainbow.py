from datetime import datetime
from pymirror.pmmodule import PMModule
from pymirror.pmscreen import PMGfx

class Rainbow(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.first_time = True

	def render(self):
		gfx = self.gfx
		x = gfx.x0
		y = gfx.y0
		width = int(gfx.x1 - gfx.x0)
		height = int(gfx.y1 - gfx.y0)
		red = 0
		green = 0
		blue = 0
		for r in range(256):
			gfx.color = (r, 0, 0)  # Red to black
			self.screen.line(gfx, x + r, y, x + r, y + height)

	def exec(self):
		if self.first_time:
			self.first_time = False
			self.render()
			return

	def onEvent(self, event):
		pass

