import time
from datetime import datetime
from pymirror.pmmodule import PMModule
from pymirror.pmscreen import PMGfx

class Clock(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self.gfx.set_font("DejaVuSans", 64)


	def render(self):
		now = datetime.now()
		formatted = now.strftime("%I:%M:%S %p")
		gfx = self.gfx
		self.screen.text_box(gfx, formatted, gfx.x0, gfx.y0, gfx.x1, gfx.y1)

	def exec(self):
		self.render()

	def onEvent(self, event):
		pass

