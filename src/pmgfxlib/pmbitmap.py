##
## This is the PyMirror implementation-independent bitmap class.
## This implementation uses the Pillow library for image manipulation.
## It's intended that other bitmap implementations can be created
## for different graphics libraries.
## But the interface should remain the same.
##
## PMBitmap is the lowest level graphcics class in PyMirror.
##

from PIL import Image, ImageDraw, ImageColor

from pymirror.pmlogger import trace
from .pmgfx import PMGfx

CENTER = 0
BOTTOM = 1
TOP = 2
LEFT = 1
RIGHT = 2

@trace
class PMBitmap:
    def __init__(self, width=None, height=None):
        self.gfx = PMGfx()
        if width is None or height is None:
            ## create a PMBitmap but don't allocate an underlying PIL Bitmap
            return
        self._img = Image.new("RGB", (width, height), 0)
        self._draw = ImageDraw.Draw(self._img)

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
            self._draw.text((x0, y0), msg, font=self.gfx.font, stroke_fill=self.gfx._text_color, fill=self.gfx._text_bg_color)
        else:
            # Use the specified fill color
            self._draw.text((x0, y0), msg, font=self.gfx.font, stroke_fill=self.gfx._text_color, fill=fill)

    def text_box(self, lines: str | list[str], valign: str = "center", halign: str = "center") -> None:
        ## renders text in the entire bitmap area
        ## if you want a cliprect, create a PMBitmap with the cliprect size
        ## then render it and paste it into the parent PMBitmap
        self.clear()
        if lines == None:
            return
        if isinstance(lines, str):
            lines = [lines]
        valign = {"center": CENTER, "top": TOP, "bottom": BOTTOM}[valign or "center"]
        halign = {"center": CENTER, "left": LEFT, "right": RIGHT}[halign or "center"]
        if valign == CENTER: 
            text_y0 = int((self.gfx.height - self.gfx.font.height * len(lines)  - self.gfx.font.baseline ) / 2)
        elif valign == TOP: 
            text_y0 = 0
        elif valign == BOTTOM: 
            text_y0 = int(self.gfx.height - self.gfx.font.height * len(lines) - self.gfx.font.baseline)
        else: 
            print(f"Invalid valign '{type(valign), valign}' in text_box, using 'center' instead.")

        for line in lines:
            (x_min, baseline, width, font_height) = self.gfx.font.getbbox(line)
            if halign == CENTER: 
                text_x0 = int((self.gfx.width - width) / 2)
            elif halign == LEFT: 
                text_x0 = 0
            elif halign == RIGHT: 
                text_x0 = int(self.gfx.width - width)
            else: 
                print(f"Invalid halign '{type(halign), halign}' in text_box, using 'center' instead.")
            self._draw.text((text_x0, text_y0), line, stroke_fill=self.gfx._text_color, fill=self.gfx._text_bg_color, font=self.gfx.font._font)
            text_y0 += font_height + baseline

    def paste(self, src: 'PMBitmap', x0 = None, y0 = None) -> None:
        if x0 is None: x0 = self.gfx.x0
        if y0 is None: y0 = self.gfx.y0
        self._img.paste(src._img, (x0, y0))

