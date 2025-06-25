from datetime import datetime
from pymirror.pmmodule import PMModule
from pymirror.pmscreen import PMGfx

class Rainbow(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.first_time = True

	def render(self, force: bool = False) -> bool:
		print("Rainbow render")
		gfx = self.gfx
		x = gfx.x0
		y = gfx.y0
		width = int(gfx.x1 - gfx.x0)
		height = int(gfx.y1 - gfx.y0)
		for r in range(256):
			gfx.color = (r, 0, 0)  # Red to black
			self.screen.line(gfx, (x, y, x, y + height))
			x += 1
		for g in range(256):
			gfx.color = (0, g, 0)  # Green to black
			self.screen.line(gfx, (x, y, x, y + height))
			x += 1
		for b in range(256):
			gfx.color = (0, 0, b)  # Blue to black
			self.screen.line(gfx, (x, y, x, y + height))
			x += 1
		return True

	def exec(self):
		if self.first_time:
			self.first_time = False
			return 1
		return 0

	def onEvent(self, event):
		pass

