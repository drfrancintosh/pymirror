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
		gfx.text_bg_color = gfx.bg_color
		self.screen.text_box(gfx, self.curr_time,
			(gfx.x0 + self.moddef.x_offset, gfx.y0 + self.moddef.y_offset,
			gfx.x1 + self.moddef.x_offset, gfx.y1 + self.moddef.y_offset))
		return 1

	def exec(self):
		self.curr_time = datetime.now().strftime(self.date_format)
		if self.last_time == self.curr_time: return 0
		self.render()
		self.last_time = self.curr_time
		return 1

	def onEvent(self, event):
		pass

