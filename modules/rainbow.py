from datetime import datetime
from pymirror.pmmodule import PMModule
from pymirror.pmscreen import PMGfx

class Rainbow(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
	
	def render(self):
		gfx = self.gfx
		x = gfx.x0
		y = gfx.y0
		width = gfx.x1 - gfx.x0
		height = gfx.y1 - gfx.y0
		red = 0
		green = 0
		blue = 0
		for w in range(width):
			for h in range(height):
				gfx.color = (red % 256, green % 256, blue % 256)
				self.screen.rect(gfx, x + w, y + h, 5, 5, fill=gfx.color)
				red += 1
				if red >= 256:
					red = 0
					green += 1
				if green >= 256:
					green = 0
					blue += 1
				if blue >= 256:
					blue = 0

	def exec(self):
		self.render()

	def onEvent(self, event):
		pass

