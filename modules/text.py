from pymirror import PMModule, PMFader
from pymirror import SafeNamespace
from pymirror.pmgfx import color_from_tuple, color_to_tuple

class Text(PMModule):
	def __init__(self, pm, config: SafeNamespace):
		super().__init__(pm, config)
		self._text = config.text
		self.text = self._text.text
		self.last_text = None
		self.direction = 0.10
		self.fader = PMFader("#000", "#fff", 5.0)
		self.gfx.text_color = self.fader.start()

	def render(self, force: bool = False) -> int:
		gfx = self.gfx
		self.clear_region()
		self.screen.text_box(gfx, self.text, self.gfx.rect, valign=self._text.valign, halign=self._text.halign)
		self.last_text = self.text
		return True

	def exec(self):
		if self.text != self.last_text:
			print(f"Text changed: {self.text}")
			self.fader = PMFader("#000", "#fff", 5.0)
			self.gfx.text_color = self.fader.start()
			return True
		if not self.fader.is_done(): 
			self.gfx.text_color = self.fader.next(self.gfx.text_color)
			return True
		print(f"Fader done, switching text color {self.gfx.text_color}")
		if self.gfx.text_color != 0:
			print("Text color is white, switching to black")
			self.fader = PMFader("#fff", "#000", 5.0)
			self.gfx.text_color = self.fader.start()
		else:
			print("Text color is black, switching to white")
			self.fader = PMFader("#000", "#fff", 5.0)
			self.gfx.text_color = self.fader.start()
		return True

