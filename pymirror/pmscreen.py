import time
from PIL import Image, ImageDraw
from pymirror.pmgfx import PMGfx, tocolor

class PMScreen:
    def __init__(self, config):
        self.config = config
        self.img = Image.new("I", (config.width, config.height), 0)
        self.draw = ImageDraw.Draw(self.img)
        self.gfx = PMGfx()
        self.gfx.width, self.gfx.height = self.img.size
        self.gfx.rect = (0, 0, self.gfx.width-1, self.gfx.height-1)
        self.set_flush(False) ## do not flush by default
        self.gfx.color = self.config.color or (255, 255, 255)  # default color
        self.gfx.bg_color = self.config.bg_color or (0, 0, 0)
        self.gfx.text_color = self.config.text_color or self.gfx.color
        self.gfx.text_bg_color = self.config.text_bg_color or None
        self.gfx.line_width = self.config.line_width or 1
        self.gfx.font_name = self.config.font or "DejaVuSans.ttf"
        self.gfx.font_size = self.config.font_size or 64
        self.gfx.set_font(self.gfx.font_name, self.gfx.font_size)

        self._hard_clear()

    def _hard_clear(self):
        """Clear the framebuffer by writing zeros to it."""
        with open("/dev/fb0", "wb") as f:
            f.write(b'\x00' * (1920 * 1080 * 2))  # Assuming RGB565 format, 2 bytes per pixel

    def set_flush(self, doFlush: bool) -> None:
        self._doFlush = doFlush

    def delay(self, ms: int) -> None:
        time.sleep(ms / 1000)
        if self._doFlush: self.flush()

    def clear(self) -> None:
        self.draw.rectangle(self.gfx.rect, self.gfx.bg_color)
        if self._doFlush: self.flush()

    def line(self, gfx: PMGfx, rect: tuple):
        self.draw.line(rect, fill=gfx.color, width=gfx.line_width)
        if self._doFlush: self.flush()

    def ellipse(self, gfx: PMGfx, rect: tuple, fill=None):
        if fill:
            self.draw.ellipse(rect, outline=gfx.color, width=gfx.line_width, fill=tocolor(fill))
        else:
            if gfx.bg_color:
                self.draw.ellipse(rect, outline=gfx.color, width=gfx.line_width, fill=gfx.bg_color)
            else:
                self.draw.ellipse(rect, outline=gfx.color, width=gfx.line_width)
        if self._doFlush: self.flush()

    def circle(self, gfx: PMGfx, x0: int, y0: int, r: int, fill="__use_bg_color__"):
        bbox = (x0-r, y0-r, x0+r, y0+r)
        if fill == "__use_bg_color__":
            # Use the gfx.background color
            self.draw.ellipse(bbox, outline=gfx.color, width=gfx.line_width, fill=gfx.bg_color)
        elif fill is None:
            # No fill, just draw the outline
            self.draw.ellipse(bbox, outline=gfx.color, width=gfx.line_width)
        else:
            # Use the specified fill color
            self.draw.ellipse(bbox, outline=gfx.color, width=gfx.line_width, fill=tocolor(fill))
        if self._doFlush: self.flush()

    def rect(self, gfx: PMGfx, rect: tuple, fill="__use_bg_color__"):
        if fill == "__use_bg_color__":
            # Use the gfx.background color if specified
            self.draw.rectangle(rect, outline=gfx.color, width=gfx.line_width, fill=gfx.bg_color)
        elif fill is None:
            # No fill, just draw the outline
            self.draw.rectangle(rect, outline=gfx.color, width=gfx.line_width)
        else:
            # Use the specified fill color
            self.draw.rectangle(rect, outline=gfx.color, width=gfx.line_width, fill=tocolor(fill))
        if self._doFlush: self.flush()

    def text(self, gfx: PMGfx, msg: str, x0: int, y0: int) -> None:
        (x_min, y_min, x_max, y_max) = gfx.font.getbbox(msg)
        width = x_max - x_min
        height = y_max
        # Draw background rectangle
        if gfx.text_bg_color:
            self.draw.rectangle((x0, y0, x0 + width, y0 + height), fill=gfx.text_bg_color)
        # Draw text
        self.draw.text((x0, y0), msg, fill=gfx.text_color, font=gfx.font)
        if self._doFlush: self.flush()

    def text_box(self, gfx: PMGfx, msg: str, rect: tuple, valign: str = "center", halign: str = "center") -> None:
        x0, y0, x1, y1 = rect

        if gfx.text_bg_color is not None: self.draw.rectangle(rect, fill=gfx.text_bg_color)
        lines = _text_split(gfx, msg, rect, split_fn=_text_split_words)

        if valign == "center": text_y0 = y0 + ( _height(rect) - gfx.font_height * len(lines)) / 2 - gfx.font_baseline / 2
        elif valign == "top": text_y0 = y0 - gfx.font_baseline
        elif valign == "bottom": text_y0 = y1 - gfx.font_height * len(lines) - gfx.font_baseline
        else: print(f"Invalid valign '{valign}' in text_box, using 'center' instead.")

        for line in lines:
            (x_min, baseline, width, font_height) = gfx.font.getbbox(line)
            if halign == "center": text_x0 = x0 + (_width(rect) - width) / 2
            elif halign == "left": text_x0 = x0
            elif halign == "right": text_x0 = x1 - width
            else: print(f"Invalid halign '{halign}' in text_box, using 'center' instead.")

            self.draw.text((text_x0, text_y0), line, fill=gfx.text_color, font=gfx.font)
            text_y0 += gfx.font_height
        if self._doFlush: self.flush()

    def flush(self):
        if self.config.rotate:
            rotated = self.img.rotate(self.config.rotate, expand=False) 
            raw = rotated.tobytes("raw")
        else:
            raw = self.img.tobytes("raw")
        # Write to framebuffer
        with open("/dev/fb0", "wb") as f:
            f.write(raw[0::2])  # Write every second byte for RGB565 format

    def quit(self):
        if self._doFlush: self.flush()

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

def main():
    pms = PMScreen(1920, 1000)
    pms.gfx.color = (0, 0, 255)
    pms.clear()
    pms.line(pms.gfx, pms.gfx.rect)
    pms.gfx.color = (255, 0, 0)
    pms.gfx.bg_color = (0, 250, 0)
    pms.rect(pms.gfx, (50, 50, 200, 250)) # red with green inside
    pms.gfx.bg_color = None
    pms.rect(pms.gfx, (100, 100, 250, 300)) # red with clear inside
    pms.rect(pms.gfx, (150, 150, 300, 350), fill=(250, 0, 250)) # red with purple inside
    pms.gfx.text_color = 0xFFFF00  # yellow text
    pms.gfx.set_font("NimbusSansNarrow-Oblique", 48)
    pms.text(pms.gfx, "Hello World!", 50,60)
    pms.flush()
    pms.quit()

if __name__ == "__main__":
    main()
