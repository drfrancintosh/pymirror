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
	
	def render(self, force: bool = False) -> bool:
		gfx = self.gfx
		self.bitmap.clear()
		self.bitmap.text_box(gfx, self.curr_time,
			(0, 0, gfx.width, gfx.height),
			halign=self._clock.halign,
			valign=self._clock.valign)
		self.last_time = self.curr_time
		return True

	def exec(self) -> bool:
		# if date_format includes "%W" or "%U", update the week number
		# all this ceremony because %W and %U are zero-based and we must add 1 to them
		if self.date_format and "%W" in self.date_format:
			self.date_format = self.date_format.replace("%W", "_W_")
		if self.date_format and "%U" in self.date_format:
			self.date_format = self.date_format.replace("%U", "_U_")
		self.curr_time = datetime.now().strftime(self.date_format)
		if self.date_format and "_W_" in self.date_format:
			week_number = int(datetime.now().strftime("%W")) + 1
			self.curr_time = self.curr_time.replace("_W_", f"{week_number:02d}")
		if self.date_format and "_U_" in self.date_format:
			week_number = int(datetime.now().strftime("%U")) + 1
			self.curr_time = self.curr_time.replace("_U_", f"{week_number:02d}")
		return self.curr_time != self.last_time 
	
	def onEvent(self, event):
		pass

