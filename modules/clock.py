import time
from datetime import datetime
from pymirror.pmmodule import PMModule
from pymirror.pmscreen import PMGfx

class Clock(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		if not self.gfx.font_name: self.gfx.font_name = "DejaVuSans"
		if not self.gfx.font_size: self.gfx.font_size = 32
		self.gfx.set_font(self.gfx.font_name, self.gfx.font_size)
		self.date_format = "%I:%M:%S %p"
		if config.date_format: self.date_format = config.date_format

	def render(self):
		now = datetime.now()
		formatted = now.strftime(self.date_format)
		gfx = self.gfx
		self.screen.text_box(gfx, formatted,
			gfx.x0 + self.x_offset, gfx.y0 + self.y_offset,
			gfx.x1 + self.x_offset, gfx.y1 + self.y_offset)

	def exec(self):
		self.render()

	def onEvent(self, event):
		pass

