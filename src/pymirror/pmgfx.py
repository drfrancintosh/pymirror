from dataclasses import dataclass
import time
from typing import Optional, Any
from PIL import ImageFont

from pymirror.utils import tocolor, fromcolor

FONT_LIST = []  # List to hold font paths

@dataclass
class PMGfx:
    rect: tuple = (0, 0, 0, 0)
    ## colors are stored as integers for efficiency
    ## use the accessors to convert to/from hex strings
    _color: int = tocolor("#fff")  # default color
    _bg_color: int = tocolor("#000")  # default background color
    _text_color: int = tocolor("#fff")  # default text color
    _text_bg_color: int = None  # default text background color
    line_width: int = 1
    font_name: str = "DejaVuSans"  # default font name
    font_size: int = 64
    antialias: bool = True
    font: Optional[ImageFont.FreeTypeFont] = None
    _font_metrics: tuple = (0, 0, 0, 0)  # (offset, baseline, width, height)

    def __post_init__(self):
        self.set_font(self.font_name, self.font_size)

    @property
    def color(self):
        return fromcolor(self._color)

    @color.setter
    def color(self, value):
        self._color = tocolor(value)

    @property
    def bg_color(self):
        return fromcolor(self._bg_color)

    @bg_color.setter
    def bg_color(self, value):
        self._bg_color = tocolor(value)

    @property
    def text_color(self):
        return fromcolor(self._text_color)

    @text_color.setter
    def text_color(self, value):
        self._text_color = tocolor(value)

    @property
    def text_bg_color(self):
        return fromcolor(self._text_bg_color)

    @text_bg_color.setter
    def text_bg_color(self, value):
        self._text_bg_color = tocolor(value)

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

    @property
    def font_height(self) -> int:
        return self._font_metrics[3]

    @property
    def font_width(self) -> int:
        return self._font_metrics[2]

    @property
    def font_offset(self) -> int:
        return self._font_metrics[0]

    @property
    def font_baseline(self) -> int:
        return self._font_metrics[1]
    
    @property
    def font_metrics(self) -> tuple:
        return self._font_metrics

    def set_font(self, font_name: str, pitch: int = 64) -> bool:
        if not pitch:
            pitch = 64
        try:
            for font_path in FONT_LIST:
                if font_name in font_path:
                    self.font = ImageFont.truetype(font_path, size=pitch)
                    self.font_name = font_name
                    self.font_size = int(pitch)
                    self._font_metrics = self.font.getbbox("M")
                    return True  # successfully set the font
        except Exception as e:
            print(f"Error setting font '{font_path}': {e}")
        return False

def _read_fonts() -> None:
    with open("./fontlist.txt", "r") as f:
        fonts = f.read().splitlines()
        for font_path in fonts:
            # split line at # discard the rest
            font_path = font_path.split("#")[0].strip()
            if not font_path:
                continue  # skip empty lines
            # split after the : # discard the rest
            font_path = font_path.split(":")[0].strip()
            if not font_path:
                continue  # skip empty lines
            FONT_LIST.append(font_path)

_read_fonts()