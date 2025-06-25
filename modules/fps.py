from datetime import datetime
from pymirror.pmmodule import PMModule

class Fps(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.last_time = datetime.now()

	def render(self, force: bool = False) -> bool:
		now = datetime.now()
		delta = now - self.last_time
		self.last_time = now
		fps = 1 / delta.total_seconds() if delta.total_seconds() > 0 else 0
		text_box = self.screen.text_box
		self.clear_region()
		text_box(self.gfx, f"FPS: {fps:.2f}", self.gfx.rect, valign=self.config.valign, halign=self.config.halign)
		return True

	def exec(self):
		return True

	def onEvent(self, event):
		pass			

