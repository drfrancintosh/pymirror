from PIL import Image, ImageDraw
from pymirror.pmgfx import PMGfx, tocolor

class PMBitmap:
    def __init__(self, width=None, height=None, bg_color=0):
        if width is None or height is None:
            return
        self.img = Image.new("I", (width, height), bg_color)
        self.draw = ImageDraw.Draw(self.img)
        self._bg_color = bg_color

    def set_img(self, img: Image) -> None:
        """ Set the bitmap to an Image object """
        self.img = img

    def clear(self) -> None:
        self.draw.rectangle((0, 0, self.img.width, self.img.height), fill=self._bg_color)

    def line(self, gfx: PMGfx, rect: tuple):
        self.draw.line(rect, fill=gfx._color, width=gfx.line_width)

    def ellipse(self, gfx: PMGfx, rect: tuple, fill=None):
        if fill:
            self.draw.ellipse(rect, outline=gfx._color, width=gfx.line_width, fill=tocolor(fill))
        else:
            if gfx._bg_color:
                self.draw.ellipse(rect, outline=gfx._color, width=gfx.line_width, fill=gfx._bg_color)
            else:
                self.draw.ellipse(rect, outline=gfx._color, width=gfx.line_width)

    def circle(self, gfx: PMGfx, x0: int, y0: int, r: int, fill="__use_bg_color__"):
        bbox = (x0-r, y0-r, x0+r, y0+r)
        if fill == "__use_bg_color__":
            # Use the gfx.background color
            self.draw.ellipse(bbox, outline=gfx._color, width=gfx.line_width, fill=gfx._bg_color)
        elif fill == None:
            # No fill, just draw the outline
            self.draw.ellipse(bbox, outline=gfx._color, width=gfx.line_width)
        else:
            # Use the specified fill color
            self.draw.ellipse(bbox, outline=gfx._color, width=gfx.line_width, fill=tocolor(fill))

    def rect(self, gfx: PMGfx, rect: tuple, fill="__use_bg_color__"):
        if fill == "__use_bg_color__":
            # Use the gfx.background color if specified
            self.draw.rectangle(rect, outline=gfx._color, width=gfx.line_width, fill=gfx._bg_color)
        elif fill == None:
            # No fill, just draw the outline
            self.draw.rectangle(rect, outline=gfx._color, width=gfx.line_width)
        else:
            # Use the specified fill color
            self.draw.rectangle(rect, outline=gfx._color, width=gfx.line_width, fill=tocolor(fill))

    def text(self, gfx: PMGfx, msg: str, x0: int, y0: int) -> None:
        (x_min, y_min, x_max, y_max) = gfx.font.getbbox(msg)
        width = x_max - x_min
        height = y_max
        # Draw background rectangle
        if gfx._text_bg_color:
            self.draw.rectangle((x0, y0, x0 + width, y0 + height), fill=gfx._text_bg_color)
        # Draw text
        self.draw.text((x0, y0), msg, fill=gfx._text_color, font=gfx.font)

    def text_box(self, gfx: PMGfx, msg: str, rect: tuple, valign: str = "center", halign: str = "center", wrap=None) -> None:
        x0, y0, x1, y1 = rect
        text_x0 = x0
        text_y0 = y0

        if valign == None: valign = "center"
        if halign == None: halign = "center"

        if gfx._text_bg_color is not None: 
            self.draw.rectangle(rect, fill=gfx._text_bg_color)
        if msg == None:
            msg = ""
        if wrap == "chars":
            lines = _text_split(gfx, msg, rect, split_fn=_text_split_chars)
        elif wrap == "words":
            lines = _text_split(gfx, msg, rect, split_fn=_text_split_words)
        else:
            lines = msg.splitlines()
            lines = [line.strip() for line in lines if line.strip()]
        if valign == "center": text_y0 = y0 + ( _height(rect) - gfx.font_height * len(lines)) / 2 - gfx.font_baseline / 2
        elif valign == "top": text_y0 = y0 - gfx.font_baseline
        elif valign == "bottom": text_y0 = y1 - gfx.font_height * len(lines) - gfx.font_baseline
        else: print(f"Invalid valign '{type(valign), valign}' in text_box, using 'center' instead.")
        if text_y0 < y0:
            text_y0 = y0
        for line in lines:
            (x_min, baseline, width, font_height) = gfx.font.getbbox(line)
            if halign == "center": text_x0 = x0 + (_width(rect) - width) / 2
            elif halign == "left": text_x0 = x0
            elif halign == "right": text_x0 = x1 - width
            else: print(f"Invalid halign '{type(halign), halign}' in text_box, using 'center' instead.")
            text_x0 = int(text_x0)
            text_y0 = int(text_y0)
            self.draw.text((text_x0, text_y0), line, fill=gfx._text_color, font=gfx.font)
            text_y0 += gfx.font_height

    def paste(self, gfx, src: 'PMBitmap', x0 = None, y0 = None) -> None:
        if x0 is None: x0 = gfx.x0
        if y0 is None: y0 = gfx.y0
        self.img.paste(src.img, (x0, y0))

def _height(rect: tuple) -> int:
    return rect[3] - rect[1]

def _width(rect: tuple) -> int:
    return rect[2] - rect[0]

def _fit_text_chars(gfx, msg: str, rect: tuple) -> int:
    n = 0
    last_n = 0
    max = len(msg)
    while True:
        if n >= max:
            return n
        last_n = n
        width = gfx.font.getbbox(msg[:n])[2]  # Get width of the text
        if width > _width(rect):
            return last_n
        n += 1

def _fit_text_words(gfx, words: list[str], rect: tuple) -> int:
    n = 0
    last_n = 0
    max = len(words)
    while True:
        if n > max: return n
        test_words = words[:n]
        test_line = " ".join(test_words)
        width = gfx.font.getbbox(test_line)[2]  # Get width of the text
        if width >= _width(rect): return last_n
        last_n = n
        n += 1

def _text_split_words(gfx, s, rect: tuple) -> list[str]:
    words = s.split()
    n = 0
    end = len(words)
    lines = []
    while True:
        test_words = words[n:]
        l = _fit_text_words(gfx, test_words, rect)
        if l == 0: break
        lines.append(" ".join(words[n:n+l]))
        n += l
        if n >= end: break
    return lines

def _text_split_chars(gfx, s, rect: tuple) -> list[str]:
    n = 0
    lines = []
    max = len(s)
    while True:
        if n >= max:
            break
        if s[n] == ' ':
            n += 1
            continue
        l = _fit_text_chars(gfx, s[n:], rect)
        if l == 0:
            break
        lines.append(s[n:n+l])
        n += l
    return lines

def _text_split(gfx, s, rect:tuple, split_fn=None) -> list[str]:
    results = []
    height = 0
    for s in s.splitlines():
        if height >= _height(rect):
            break
        s = s.strip()
        split_lines = split_fn(gfx, s, rect)
        results.extend(split_lines)
        height += gfx.font_height
    return results