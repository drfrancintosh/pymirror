import copy
from dataclasses import dataclass

from pymirror.pmmodule import PMModule
from pymirror.pmgfx import PMFader
from pymirror.utils import _NONE_PROXY

@dataclass
class PMCardText:
		font_name: str = None
		font_size: int = 24
		text_color: str = "#fff"
		text_bg_color: str = "#000"
		height: int = 48
		width: int = 0
		halign: str = "center"
		valign: str = "center"
		fade_in: float = 0.0
		fade_out: float = 0.0
		fader: PMFader = None
		text: str = ""
		last_text: str = ""

		def is_dirty(self) -> bool:
			""" Check if the text has changed. """
			return self.text != self.last_text

		def is_fading_in(self) -> bool:
			if self.fade_in > 0.0:
				if not self.fader or self.fader.is_done():
					self.fader = PMFader(self.text_bg_color, self.text_color, self.fade_in)
					self.text_color = self.fader.start()
				else:
					self.text_color = self.fader.next(self.text_color)
			return not self.fader or self.fader.is_done() ## returns True if the fade in is done

		def is_fading(self, fade_value: float) -> bool:
			if fade_value > 0.0:
				if not self.fader or self.fader.is_done():
					self.fader = PMFader(self.text_bg_color, self.text_color, fade_value)
					self.text_color = self.fader.start()
				else:
					self.text_color = self.fader.next(self.text_color)
			return not self.fader or self.fader.is_done() ## returns True if the fade in is done

		def is_fading_out(self) -> bool:
			if self.fade_out > 0.0:
				if not self.fader or self.fader.is_done():
					self.fader = PMFader(self.text_color, self.text_bg_color, self.fade_out)
					self.text_color = self.fader.start()
				else:
					self.text_color = self.fader.next(self.text_color)
			return not self.fader or self.fader.is_done() ## returns True if the fade out is done


class PMCard(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self._card = self.config.card
		self._card.header = PMCardText(**self._card.header.__dict__) if self._card.header else _NONE_PROXY
		self._card.body = PMCardText(**self._card.body.__dict__) if self._card.body else _NONE_PROXY
		self._card.footer = PMCardText(**self._card.footer.__dict__) if self._card.footer else _NONE_PROXY

	def update(self, header: str, body: str, footer: str) -> None:
		self._card.header.last_text = self._card.header.text
		self._card.body.last_text = self._card.body.text
		self._card.footer.last_text = self._card.footer.text
		self._card.header.text = header
		self._card.body.text = body
		self._card.footer.text = footer

	def is_dirty(self) -> bool:
		return (self._card.header.is_dirty() or
				self._card.body.is_dirty() or
				self._card.footer.is_dirty())

	def _render_text(self, msg, rect, card_text, maybe_invert_colors=False) -> int: # returns next y position
		gfx = self.gfx
		gfx2 = copy.copy(self.gfx)
		gfx2.set_font(card_text.font_name or gfx.font_name, card_text.font_size or gfx.font_size)
		gfx2.text_color = card_text.text_color or gfx.text_color
		gfx2.text_bg_color = card_text.text_bg_color or gfx.text_bg_color

		if maybe_invert_colors:
			if card_text.text_color == None and card_text.text_bg_color == None:
				## no colors were specified for the text
				## so use the default screen colors but invert them
				gfx2.text_color = gfx.text_bg_color
				gfx2.text_bg_color = gfx.text_color
		self.screen.text_box(gfx2, msg, rect, halign=card_text.halign, valign=card_text.valign)
		return rect[3] + 1 # next y position after rendering the text box

	def render(self, force: bool = False) -> bool:
		self.clear_region()
		gfx = self.gfx
		header_height = self._card.header.height or self._card.header.font_size or gfx.font_size
		footer_height = self._card.footer.height or self._card.footer.font_size or gfx.font_size
		next_y0 = gfx.y0
		if (self._card.header):
			next_y0 = self._render_text(self._card.header.text, (gfx.x0, gfx.y0, gfx.x1, gfx.y0 + header_height), self._card.header, maybe_invert_colors=True)
		if (self._card.footer):
			next_y0 = self._render_text(self._card.body.text, (gfx.x0, next_y0, gfx.x1, gfx.y1 - footer_height), self._card.body, maybe_invert_colors=False)
			next_y0 =self._render_text(self._card.footer.text, (gfx.x0, next_y0, gfx.x1, gfx.y1), self._card.footer, maybe_invert_colors=True)
		else:
			self._render_text(self._card.body.text, (gfx.x0, next_y0, gfx.x1, gfx.y1), self._card.body, maybe_invert_colors=False)
		return True
	
	def exec(self):
		""" Check if the card has changed and needs to be re-rendered. """
		is_dirty = False
		card = self._card.body
		if card.is_dirty():
			print(f"Card text changed: {card.text} != {card.last_text}")
			if card.is_fading(card.fade_out):
				print(f"Card is fading out: {card.text} != {card.last_text}")
				card.last_text = card.text
			is_dirty = True
		else:
			print(f"Card text is not dirty: {card.text} == {card.last_text}")
			if card.is_fading(card.fade_in):
				print(f"Card is fading in: {card.text} != {card.last_text}")
				card.last_text = card.text
				is_dirty = True
		return is_dirty