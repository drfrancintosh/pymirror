from pymirror.pmmodule import PMModule
from pymirror.utils import SafeNamespace

class Text(PMModule):
	def __init__(self, pm, config: SafeNamespace):
		super().__init__(pm, config)
		self._text = config.text
		self.text = self._text.text
		self.last_text = None

	def render(self, force: bool = False) -> int:
		gfx = self.gfx
		self.bitmap.clear()
		self.bitmap.text_box(gfx, self.text, (0, 0, gfx.width, gfx.height), valign=self._text.valign, halign=self._text.halign)
		self.last_text = self.text
		return True

	def exec(self):
		return self.text != self.last_text

