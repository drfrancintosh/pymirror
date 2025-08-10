from pymirror.pmrect import PMRect
from pymirror.pmtimer import PMTimer
from pymirror.comps.pmcomponent import PMComponent
from pmgfxlib import PMBitmap
from pymirror.utils import SafeNamespace, non_null

class PMTextComp(PMComponent):
    def __init__(self, config: SafeNamespace, x0: int = None, y0: int = None, height: int = None, width: int = None):
        super().__init__(config)
        self.text = self._config.text or ""
        self.clip = non_null(self._config.clip, False)
        self.use_baseline = non_null(self._config.use_baseline, False)
        self.gfx.rect.x0 = non_null(x0, self._config.x0, 0)
        self.gfx.rect.y0 = non_null(y0, self._config.y0, 0)
        self.gfx.rect.height = non_null(height, self._config.height, self.gfx.font.height, 0)
        self.gfx.rect.width = non_null(width, self._config.width, self.gfx.font.width * len(self.text))
        self.hscroll = non_null(self._config.hscroll, False)
        self._hscroll_delay = 100
        self._hscroll_timer = PMTimer(0)
        if self.hscroll:
            self._hscroll_timer = PMTimer(self._hscroll_delay)
        self._hoffset = 0
        self._dx = -10
        self._last_text = None

    def render(self, bitmap: PMBitmap) -> None:
        bm_rect = bitmap.gfx.rect
        gfx = bitmap.gfx_push(self.gfx)
        gfx.rect = bm_rect
        lines = gfx.font.text_split(self.text, gfx.rect, gfx.wrap)
        bitmap.text_box(self.gfx.rect, lines, gfx.valign, gfx.halign, self.clip, self.use_baseline)
        bitmap.gfx_pop()
        self.clean()

    def update(self, text: str = None) -> None:
        if text is not None:
            self.text = text
        else:
            self.text = self._last_text

    def is_dirty(self) -> bool:
        """Check if the text has changed since the last render."""
        if self._hscroll_timer.is_timedout():
            self._hoffset += self._dx
            if self._hoffset < -self.gfx.rect.width:
                self._hoffset = self.gfx.rect.width
            self._hscroll_timer.set_timeout(self._hscroll_delay)
            return True
        return self.text != self._last_text

    def clean(self) -> bool:
        """Mark the text as clean, i.e., no changes since last render."""
        self._last_text = self.text
        return True