import copy
from dataclasses import dataclass

from pymirror.pmmodule import PMModule
from pymirror.utils import _NONE_PROXY, SafeNamespace

@dataclass
class PMCardText:
		font_name: str = None
		font_size: int = 24
		start_color: str = None
		text_color: str = "#000"
		text_bg_color: str = "#000"
		height: int = 48
		width: int = 0
		halign: str = "center"
		valign: str = "center"
		wrap: str = "words"  # "chars", "words", or None
		text: str = None
		last_text: str = None

		def is_dirty(self) -> bool:
			return self.text != self.last_text

class PMCard(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self._card = self._config.card
		self._card.header = PMCardText(**self._card.header.__dict__) if self._card.header else PMCardText()
		self._card.body = PMCardText(**self._card.body.__dict__) if self._card.body else PMCardText()
		self._card.footer = PMCardText(**self._card.footer.__dict__) if self._card.footer else PMCardText()
	def update(self, header: str, body: str, footer: str) -> None:
		self._card.header.text = header
		self._card.body.text = body
		self._card.footer.text = footer

	def make_clean(self) -> None:
		""" Mark the card as clean, i.e. no changes since last render """
		self._card.header.last_text = self._card.header.text
		self._card.body.last_text = self._card.body.text
		self._card.footer.last_text = self._card.footer.text

	def is_dirty(self) -> bool:
		return (self._card.header.is_dirty() or
				self._card.body.is_dirty() or
				self._card.footer.is_dirty())

	def _render_text(self, msg, rect, card_text, maybe_invert_colors=False) -> int: # returns next y position
		gfx = self.bitmap.gfx_push()
		gfx.font.set_font(card_text.font_name, card_text.font_size)
		gfx.text_color = card_text.text_color
		gfx.text_bg_color = card_text.text_bg_color

		if maybe_invert_colors:
			if card_text.text_color == None and card_text.text_bg_color == None:
				## no colors were specified for the text
				## so use the default screen colors but invert them
				gfx.text_color, gfx.text_bg_color = gfx.text_bg_color, gfx.text_color
		self.bitmap.text_box(rect, msg, halign=card_text.halign, valign=card_text.valign)
		self.bitmap.gfx_pop()
		return rect[3] + 1 # next y position after rendering the text box

	def render(self, force: bool = False) -> bool:
		self.bitmap.clear()
		gfx = self.bitmap.gfx
		header_height = self._card.header.height or self._card.header.font_size or gfx.font_size
		footer_height = self._card.footer.height or self._card.footer.font_size or gfx.font_size
		next_y0 = 0
		if (self._card.header.text):
			next_y0 = self._render_text(self._card.header.text, (0, 0, gfx.width, header_height), self._card.header, maybe_invert_colors=True)
		if (self._card.footer.text):
			next_y0 = self._render_text(self._card.body.text, (0, next_y0, gfx.width, gfx.height - footer_height), self._card.body, maybe_invert_colors=False)
			next_y0 =self._render_text(self._card.footer.text, (0, next_y0, gfx.width, gfx.height), self._card.footer, maybe_invert_colors=True)
		else:
			self._render_text(self._card.body.text, (0, next_y0, gfx.width, gfx.height), self._card.body, maybe_invert_colors=False)
		return True
	
		
	def exec(self) -> bool:
		is_dirty = self.is_dirty()
		self.make_clean()  # Mark the card as clean after checking for changes
		return is_dirty
