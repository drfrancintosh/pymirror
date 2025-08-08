from pymirror.pmrect import PMRect
from pymirror.comps.pmcomponent import PMComponent
from pmgfxlib import PMGfx, PMBitmap
from dataclasses import dataclass
from pymirror.utils import SafeNamespace, _height, _width
from pymirror.pmconstants import PMConstants

@dataclass
class PMTextConfig:
    font_name: str = PMConstants.font_name
    font_size: int = PMConstants.font_size
    text_color: str = PMConstants.text_color
    text_bg_color: str = PMConstants.text_bg_color
    x0: int = 0
    y0: int = 0
    height: int = PMConstants.font_size
    width: int = PMConstants.font_size * 20
    halign: str = PMConstants.halign
    valign: str = PMConstants.valign
    wrap: str = PMConstants.wrap  # "chars", "words", or None
    text: str = ""

class PMTextComp(PMComponent):
    def __init__(self, config: SafeNamespace):
        self._config = PMTextConfig(**config.__dict__)
        self._config.height = int(self._config.height)
        self._config.width = int(self._config.width)
        self._gfx = PMGfx()
        self._update_rect()
        self._gfx.text_color = self._config.text_color
        self._gfx.text_bg_color = self._config.text_bg_color
        self._gfx.font.set_font(self._config.font_name, self._config.font_size)
        self._gfx.halign = self._config.halign
        self._gfx.valign = self._config.valign
        self._gfx.wrap = self._config.wrap
        self.text = self._config.text

    def _update_rect(self):
        """Set the rectangle for the text component based on its configuration."""
        self._gfx.rect = PMRect(
            self._gfx.rect.x0,
            self._gfx.rect.y0,
            self._gfx.rect.x0 + self._config.width - 1,
            self._gfx.rect.y0 + self._config.height - 1
        )
    def render(self, bitmap: PMBitmap) -> None:
        bitmap.gfx_push(self._gfx)
        bitmap.text_box(self._gfx.rect, self.text, self._gfx.valign, self._gfx.halign)
        bitmap.gfx_pop()