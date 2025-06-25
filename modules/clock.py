from datetime import datetime
from pymirror.pmmodule import PMModule, PMModuleDef
from pymirror.safe_namespace import SafeNamespace

class Clock(PMModule):
	def __init__(self, pm, moddef: PMModuleDef, config: SafeNamespace):
		super().__init__(pm, moddef, config)
		self.date_format = "%I:%M:%S %p"
		self.date_format = config.date_format if config.date_format else "%I:%M:%S %p"
		self.last_time = None
		self.curr_time = datetime.now().strftime(self.date_format)
	
	def render(self, force: bool = False) -> int:
		if not force and self.last_time == self.curr_time: return 0
		gfx = self.gfx
		self.rect(gfx, gfx.rect)
		self.screen.text_box(gfx, self.curr_time,
			(gfx.x0 + self.moddef.x_offset, gfx.y0 + self.moddef.y_offset,
			gfx.x1 + self.moddef.x_offset, gfx.y1 + self.moddef.y_offset))
		self.last_time = self.curr_time
		return 1

	def exec(self):
		self.curr_time = datetime.now().strftime(self.date_format)
		if self.last_time == self.curr_time: return 0
		return 1

	def onEvent(self, event):
		pass

