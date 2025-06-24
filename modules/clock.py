from datetime import datetime
from pymirror.pmmodule import PMModule
from pymirror.pmscreen import PMGfx

class Clock(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.date_format = "%I:%M:%S %p"
		if config.date_format: self.date_format = config.date_format

	def render(self):
		now = datetime.now()
		date_str = now.strftime(self.date_format)
		gfx = self.gfx
		self.screen.text_box(gfx, date_str,
			gfx.x0 + self.x_offset, gfx.y0 + self.y_offset,
			gfx.x1 + self.x_offset, gfx.y1 + self.y_offset)

	def exec(self):
		self.render()

	def onEvent(self, event):
		pass

