from datetime import datetime
from pymirror.pmmodule import PMModule, PMModuleDef
from pymirror.utils import SafeNamespace

class Text(PMModule):
	def __init__(self, pm, moddef: PMModuleDef, config: SafeNamespace):
		super().__init__(pm, moddef, config)
		self.text = config.text
		self.last_text = None
	
	def render(self, force: bool = False) -> int:
		gfx = self.gfx
		self.clear_region()
		self.screen.text_box(gfx, self.text, self.gfx.rect, valign=self.config.valign, halign=self.config.halign)
		self.last_text = self.text
		return True

	def exec(self):
		return self.last_text != self.text

	def onEvent(self, event):
		pass

