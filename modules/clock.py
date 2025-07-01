from datetime import datetime
from pymirror.pmmodule import PMModule, PMModuleDef
from pymirror.utils import SafeNamespace

class Clock(PMModule):
	def __init__(self, pm, config: SafeNamespace):
		super().__init__(pm, config)
		self._clock = config.clock
		self.date_format = "%I:%M:%S %p"
		self.date_format = self._clock.date_format if self._clock.date_format else "%I:%M:%S %p"
		self.last_time = None
		self.curr_time = datetime.now().strftime(self.date_format)
	
	def render(self, force: bool = False) -> int:
		if not force and self.last_time == self.curr_time: return 0
		gfx = self.gfx
		self.bitmap.clear()
		self.bitmap.text_box(gfx, self.curr_time,
			(0, 0, gfx.width, gfx.height),
			halign=self._clock.halign,
			valign=self._clock.valign)
		self.last_time = self.curr_time
		return 1

	def exec(self):
		self.curr_time = datetime.now().strftime(self.date_format)
		if self.last_time == self.curr_time: return 0
		return 1

	def onEvent(self, event):
		pass

