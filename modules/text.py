from datetime import datetime
from pymirror.pmmodule import PMModule, PMModuleDef
from pymirror.utils import SafeNamespace

class Text(PMModule):
	def __init__(self, pm, config: SafeNamespace):
		super().__init__(pm, config)
		self._text = config.text
		self.text = self._text.text
		self.last_text = None
	
	def render(self, force: bool = False) -> int:
		gfx = self.gfx
		self.clear_region()
		self.screen.text_box(gfx, self.text, self.gfx.rect, valign=self._text.valign, halign=self._text.halign)
		self.last_text = self.text
		return True

	def exec(self):
		return self.last_text != self.text

	def onEvent(self, event):
		pass

