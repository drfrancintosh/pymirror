from pymirror.pmmodule import PMModule
from pymirror.utils import SafeNamespace
from pymirror.comps.pmtextcomp import PMTextComp

class TextModule(PMModule):
	def __init__(self, pm, config: SafeNamespace):
		super().__init__(pm, config)
		self._text = PMTextComp(config.text)
		if config.text.width == None:
			self._text._config.width = self.bitmap.gfx.width
		if not config.text.height:
			self._text._config.height = self.bitmap.gfx.height
		self._text._update_rect()
		self.last_text = None

	def render(self, force: bool = False) -> int:
		self._text.render(self.bitmap)
		self.last_text = self._text.text
		return True

	def exec(self):
		return self._text.text != self.last_text

