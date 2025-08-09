from dataclasses import dataclass, fields

from pymirror.pmrect import PMRect
from pymirror.utils import from_dict
from .pmfont import PMFont
from .pmutils import to_color

@dataclass
class PMGfx:
    ## instance variables
    _rect: PMRect = PMRect(0, 0, 0, 0)
    _color: tuple = (255, 255, 255) 
    _bg_color: tuple = (0, 0, 0) 
    _text_color: tuple = (255, 255, 255)
    _text_bg_color: tuple = None  
    line_width: int = 1
    font_name: str = "DejaVuSans"
    font_size: int = 64
    font: PMFont = None
    wrap: str = "words"  # "chars", "words", or None
    halign: str = "center"  # "left", "center", "right"
    valign: str = "center"

    @classmethod
    def from_dict(cls, config: dict):
        valid_fields = {f.name for f in fields(cls)}
        filtered_dict = {k: v for k, v in config.items() if k in valid_fields}
        gfx = cls(**filtered_dict)
        gfx.rect = PMRect.from_string(config.get('rect', "0,0,0,0"))
        gfx.color = config.get('color', (255, 255, 255))
        gfx.bg_color = config.get('bg_color', (0, 0, 0))
        gfx.text_color = config.get('text_color', (255, 255, 255))
        gfx.text_bg_color = config.get('text_bg_color', None)
        gfx.set_font(gfx.font_name, gfx.font_size)
        return gfx

    def set_font(self, name: str, size: int) -> None:
        """Set the font for the graphics context."""
        self.font_name = name
        self.font_size = size
        self.font = PMFont(name, size)

    @property
    def rect(self) -> PMRect:
        return self._rect
    
    @rect.setter
    def rect(self, value: PMRect) -> None:
        if isinstance(value, PMRect):
            self._rect = value
        elif isinstance(value, tuple) and len(value) == 4:
            self._rect = PMRect(*value)
        else:
            raise TypeError("rect must be an instance of PMRect")

    @property
    def color(self) -> tuple[int, int, int]:
        return self._color

    @color.setter
    def color(self, value: str | tuple[int, int, int]) -> None:
        if isinstance(value, str):
            self._color = to_color(value)
        else:
            self._color = value

    @property
    def bg_color(self) -> tuple[int, int, int]:
        return self._bg_color

    @bg_color.setter
    def bg_color(self, value: str | tuple[int, int, int]) -> None:
        if isinstance(value, str):
            self._bg_color = to_color(value)
        else:
            self._bg_color = value

    @property
    def text_color(self) -> tuple[int, int, int]:
        return self._text_color

    @text_color.setter
    def text_color(self, value: str | tuple[int, int, int]) -> None:
        if isinstance(value, str):
            self._text_color = to_color(value)
        else:
            self._text_color = value

    @property
    def text_bg_color(self) -> tuple[int, int, int]:
        return self._text_bg_color

    @text_bg_color.setter
    def text_bg_color(self, value: str | tuple[int, int, int]) -> None:
        if isinstance(value, str):
            self._text_bg_color = to_color(value)
        else:
            self._text_bg_color = value

    @property
    def x0(self):
        return self.rect[0]

    @property
    def y0(self):
        return self.rect[1]

    @property
    def x1(self):
        return self.rect[2]

    @property
    def y1(self):
        return self.rect[3]

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    @width.setter
    def width(self, value: int):
        self.rect.width = value

    @height.setter
    def height(self, value: int):
        self.rect.height = value

