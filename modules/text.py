from pymirror.pmmodule import PMModule
from pymirror.utils import SafeNamespace
from pymirror.pmgfx import PMFader

class Text(PMModule):
	def __init__(self, pm, config: SafeNamespace):
		super().__init__(pm, config)
		self._text = config.text
		self.text = self._text.text
		self.last_text = None
		self.fader = PMFader("#000", "#fff", 5.0)
		self.gfx.text_color = self.fader.start()

	def render(self, force: bool = False) -> int:
		gfx = self.gfx
		self.clear_region()
		self.screen.text_box(gfx, self.text, self.gfx.rect, valign=self._text.valign, halign=self._text.halign)
		self.last_text = self.text
		return True

	def exec(self):
		if not self.fader.is_done():
			self.gfx.text_color = self.fader.next(self.gfx.text_color)
			return True
		return self.text != self.last_text

