import copy

from pymirror.pmmodule import PMModule
from pymirror.utils import SafeNamespace
from dataclasses import dataclass

@dataclass
class PMCardText:
		font_name: str = None
		font_size: int = 24
		text_color: str = "#000"
		text_bg_color: str = "#f00"
		height: int = 48
		width: int = 0
		halign: str = "center"
		valign: str = "center"

class PMCard(PMModule):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self._card = self.config.card
		self._card.header = PMCardText(**self._card.header.__dict__) if self._card.header else PMCardText()
		self._card.body = PMCardText(**self._card.body.__dict__) if self._card.body else PMCardText()
		self._card.footer = PMCardText(**self._card.footer.__dict__) if self._card.footer else PMCardText()
		self.header = None
		self.body = None
		self.footer = None
		self.last_header = None
		self.last_body = None
		self.last_footer = None

	def update(self, header: str, body: str, footer: str) -> None:
		self.last_header = self.header
		self.last_body = self.body 
		self.last_footer = self.footer
		self.header = header
		self.body = body
		self.footer = footer

	def has_changed(self) -> bool:
		return self.header != self.last_header or self.body != self.last_body or self.footer != self.last_footer

	def _render_text(self, msg, rect, font_info, maybe_invert_colors=False) -> int: # returns next y position
		gfx = self.gfx
		gfx2 = copy.copy(self.gfx)
		gfx2.set_font(font_info.font_name or gfx.font_name, font_info.font_size or gfx.font_size)
		gfx2.text_color = font_info.text_color or gfx.text_color
		gfx2.text_bg_color = font_info.text_bg_color or gfx.text_bg_color

		if maybe_invert_colors:
			if font_info.text_color == None and font_info.text_bg_color == None:
				## no colors were specified for the text
				## so use the default screen colors but invert them
				gfx2.text_color = gfx.text_bg_color
				gfx2.text_bg_color = gfx.text_color
		self.screen.text_box(gfx2, msg, rect, halign=font_info.halign, valign=font_info.valign)
		return rect[3] + 1 # next y position after rendering the text box

	def render(self, force: bool = False) -> bool:
		self.clear_region()
		gfx = self.gfx
		header_height = self._card.header.height or self._card.header.font_size or gfx.font_size
		footer_height = self._card.footer.height or self._card.footer.font_size or gfx.font_size
		next_y0 = gfx.y0
		if (self.header):
			next_y0 = self._render_text(self.header, (gfx.x0, gfx.y0, gfx.x1, gfx.y0 + header_height), self._card.header, maybe_invert_colors=True)
		if (self.footer):
			next_y0 = self._render_text(self.body, (gfx.x0, next_y0, gfx.x1, gfx.y1 - footer_height), self._card.body, maybe_invert_colors=False)
			next_y0 =self._render_text(self.footer, (gfx.x0, next_y0, gfx.x1, gfx.y1), self._card.footer, maybe_invert_colors=True)
		else:
			self._render_text(self.body, (gfx.x0, next_y0, gfx.x1, gfx.y1), self._card.body, maybe_invert_colors=False)
		return True
	