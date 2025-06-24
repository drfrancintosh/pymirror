from datetime import datetime
from pymirror.pmmodule import PMModule
from pymirror.pmscreen import PMGfx

class Clock(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.date_format = "%I:%M:%S %p"
		if config.date_format: self.date_format = config.date_format
		self.last_time = None
		self.curr_time = datetime.now().strftime(self.date_format)
	
	def render(self):
		gfx = self.gfx
		self.screen.text_box(gfx, self.curr_time,
			gfx.x0 + self.x_offset, gfx.y0 + self.y_offset,
			gfx.x1 + self.x_offset, gfx.y1 + self.y_offset)

	def exec(self):
		self.curr_time = datetime.now().strftime(self.date_format)
		if self.last_time == self.curr_time: return
		self.render()
		self.last_time = self.curr_time

	def onEvent(self, event):
		pass

