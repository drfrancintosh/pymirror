from datetime import datetime
from pymirror.pmmodule import PMModule
from pymirror.pmscreen import PMGfx

class Rainbow(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.first_time = True

	def render(self, force: bool = False) -> bool:
		gfx = self.gfx
		x = gfx.x0
		y = gfx.y0
		width = int(gfx.x1 - gfx.x0)
		height = int(gfx.y1 - gfx.y0)
		dw = width / 3 / 256
		dx = 0
		x = int(dx)
		for r in range(256):
			gfx.color = (r, 0, 0)  # Red to black
			self.screen.line(gfx, (x, y, x, y + height))
			dx += dw
			x = int(dx)
		for g in range(256):
			gfx.color = (0, g, 0)  # Green to black
			self.screen.line(gfx, (x, y, x, y + height))
			dx += dw
			x = int(dx)
		for b in range(256):
			gfx.color = (0, 0, b)  # Blue to black
			self.screen.line(gfx, (x, y, x, y + height))
			dx += dw
			x = int(dx)
		return True

	def exec(self):
		if self.first_time:
			self.first_time = False
			return 1
		return 0

	def onEvent(self, event):
		pass

