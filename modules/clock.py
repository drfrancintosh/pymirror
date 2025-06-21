import time
from datetime import datetime
from pymirror.pmmodule import PMModule
from pymirror.pmfont import PMFont
from pymirror.pmscreen import PMGfx

class Clock(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		pmfont = PMFont("DejaVuSans.ttf", 48)
		self.gfx.font = self.pygame.font.Font(pmfont.font_path(), 64)


	def render(self):
		now = datetime.now()
		formatted = now.strftime("%I:%M:%S %p")
		self.screen.text_box(self.gfx, formatted, self.gfx.x0, self.gfx.y0, self.gfx.x1, self.gfx.y1)

	def exec(self):
		self.render()

	def onEvent(self, event):
		pass

