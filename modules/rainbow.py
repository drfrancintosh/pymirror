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
		color = 0
		max = int(x * y)
		for i in range(max):
			gfx.color = (color % 256, (color * 2) % 256, (color * 3) % 256)
			gfx.fill_rect(x + (i % width), y + (i // width), 1, 1)
			color += 1

	def exec(self):
		self.render()

	def onEvent(self, event):
		pass

