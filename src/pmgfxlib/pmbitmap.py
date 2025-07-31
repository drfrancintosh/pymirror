##
## This is the PyMirror implementation-independent bitmap class.
## This implementation uses the Pillow library for image manipulation.
## It's intended that other bitmap implementations can be created
## for different graphics libraries.
## But the interface should remain the same.
##
## PMBitmap is the lowest level graphcics class in PyMirror.
##

import copy
from PIL import Image, ImageDraw, ImageColor

from pymirror.pmlogger import trace, _trace, _debug
from pymirror.utils import _height, _width
from .pmgfx import PMGfx

CENTER = 0
BOTTOM = 1
TOP = 2
LEFT = 1
RIGHT = 2

class PMBitmap:
    def __init__(self, width=None, height=None):
        self.gfx = PMGfx()
        self.gfx_stack = []
        if width is None or height is None:
            ## create a PMBitmap but don't allocate an underlying PIL Image
            return
        self.gfx.rect = (0, 0, width-1, height-1)
        self._img = Image.new("RGB", (width, height), 0)
        self._draw = ImageDraw.Draw(self._img)

    def gfx_push(self) -> PMGfx:
        """Push the current graphics state onto the stack."""
        self.gfx_stack.append(copy.copy(self.gfx))
        return self.gfx

    def gfx_pop(self) -> PMGfx:
        """Pop the last graphics state from the stack."""
        self.gfx = self.gfx_stack.pop()
        return self.gfx

    def clear(self) -> None:
        self._draw.rectangle((0, 0, self._img.width, self._img.height), fill=self.gfx.bg_color)

    def line(self, rect: tuple):
        self._draw.line(rect, fill=self.gfx.color, width=self.gfx.line_width)

    def ellipse(self, rect: tuple, fill=-1) -> None:
        if fill == -1:
            # Use the gfx.background color if specified
            self._draw.ellipse(rect, outline=self.gfx.color, width=self.gfx.line_width, fill=self.gfx.bg_color)
        else:
            # Use the specified fill color
            self._draw.ellipse(rect, outline=self.gfx.color, width=self.gfx.line_width, fill=fill)

    def circle(self, x0: int, y0: int, r: int, fill=-1) -> None:
        bbox = (x0-r, y0-r, x0+r, y0+r)
        self.ellipse(bbox, fill=fill)

    def rect(self, rect: tuple, fill=-1) -> None:
        if fill == -1:
            # Use the gfx.background color if specified
            self._draw.rectangle(rect, outline=self.gfx.color, width=self.gfx.line_width, fill=self.gfx.bg_color)
        else:
            # Use the specified fill color
            self._draw.rectangle(rect, outline=self.gfx.color, width=self.gfx.line_width, fill=fill)

    def text(self, msg: str, x0: int, y0: int, fill=-1) -> None:
        if fill == -1:
            # Use the gfx.background color if specified
            self._draw.text((x0, y0), msg, font=self.gfx.font._font, fill=self.gfx._text_color)
        else:
            # Use the specified fill color
            self._draw.text((x0, y0), msg, font=self.gfx.font._font, fill=fill)

    def calculate_text_box(self, lines: str) -> tuple[str, tuple[int, int]]:
        """Calculate the size of the text."""
        width = 0
        height = 0
        results = []
        for multi_line in lines:
            multi_lines = multi_line.split("\n")
            for line in multi_lines:
                results.append(line)
                (x_min, baseline, line_width, font_height) = self.gfx.font.getbbox(line)
                width = max(width, line_width)
                height += font_height
        return results, (width, height)

    def text_box(self, rect, lines: str | list[str], valign: str = "center", halign: str = "center") -> None:
        ## renders text in the entire bitmap area
        ## if you want a cliprect, create a PMBitmap with the cliprect size
        ## then render it and paste it into the parent PMBitmap
        if lines == None:
            return
        if isinstance(lines, str):
            lines = [lines]
        valign = {"center": CENTER, "top": TOP, "bottom": BOTTOM}[valign or "center"]
        halign = {"center": CENTER, "left": LEFT, "right": RIGHT}[halign or "center"]
        x0, y0, x1, y1 = rect
        if self.gfx._text_bg_color:
            self._draw.rectangle(rect, fill=self.gfx._text_bg_color)
        gfx = self.gfx
        font = self.gfx.font
        lines, (text_width, text_height) = self.calculate_text_box(lines)
        if valign == CENTER: 
            dy = _height(rect) - text_height + font.baseline
            text_y0 = y0 + int(dy / 2)
        elif valign == TOP: 
            text_y0 = y0
        elif valign == BOTTOM: 
            text_y0 = y1 - text_height
        else:
            print(f"Invalid valign '{type(valign), valign}' in text_box, using 'center' instead.")

        for multi_line in lines:
            multi_lines = multi_line.split("\n")
            for line in multi_lines:
                (x_min, baseline, width, font_height) = font.getbbox(line)
                if halign == CENTER: 
                    text_x0 = x0 + int((_width(rect) - width) / 2)
                elif halign == LEFT: 
                    text_x0 = x0
                elif halign == RIGHT: 
                    text_x0 = x0 + int(_width(rect) - width)
                else: 
                    print(f"Invalid halign '{type(halign), halign}' in text_box, using 'center' instead.")
                self._draw.text((text_x0, text_y0 - baseline), line, fill=(gfx._text_color), font=gfx.font._font)
                text_y0 += font_height
                if text_y0 >= y1:
                    break

    def paste(self, src: 'PMBitmap', x0 = None, y0 = None) -> None:
        if x0 is None: x0 = src.gfx.x0
        if y0 is None: y0 = src.gfx.y0
        self._img.paste(src._img, (x0, y0))

