from dataclasses import dataclass
from .pmfont import PMFont
from .pmutils import to_color

@dataclass
class PMGfx:
    ## instance variables
    rect: tuple = (0, 0, 0, 0)
    _color: tuple = (255, 255, 255) 
    _bg_color: tuple = (0, 0, 0) 
    _text_color: tuple = (255, 255, 255)
    _text_bg_color: tuple = None  
    line_width: int = 1
    font: PMFont = None

    def __post_init__(self):
        self.font = PMFont("DejaVuSans", 64)

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
        return self.rect[2] - self.rect[0] + 1

    @property
    def height(self):
        return self.rect[3] - self.rect[1] + 1



