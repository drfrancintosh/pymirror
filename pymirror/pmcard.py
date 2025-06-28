import copy

from pymirror.pmmodule import PMModule

class PMCard(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		print(f"PMCard: {self.moddef.name} {self.config}")
		self.header = None
		self.body = None
		self.footer = None
		self.context = {}

	def _render_text(self, msg, rect, font_info) -> int: # returns next y position
		gfx = self.gfx
		gfx2 = copy.copy(self.gfx)
		gfx2.set_font(font_info.font or gfx.font_name, font_info.font_size or gfx.font_size)
		gfx2.text_color = font_info.color or gfx.text_color
		gfx2.text_bg_color = font_info.bg_color or gfx.text_bg_color
		self.screen.text_box(gfx2, msg, rect, halign=font_info.halign, valign=font_info.valign)

	def render(self, force: bool = False) -> bool:
		self.clear_region()
		gfx = self.gfx
		header_height = self.config.card.header.font_size or gfx.font_size
		footer_height = self.config.card.footer.font_size or gfx.font_size
		self._render_text(self.header, (gfx.x0, gfx.y0, gfx.x1, gfx.y0 + header_height), self.config.card.header)
		self._render_text(self.body, (gfx.x0, gfx.y0 + header_height, gfx.x1, gfx.y1 - footer_height), self.config.card.body)
		self._render_text(self.footer, (gfx.x0, gfx.y1 - footer_height, gfx.x1, gfx.y1), self.config.card.footer)
		return True
	