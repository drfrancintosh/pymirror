import time
from PIL import Image, ImageDraw
from pymirror.pmgfx import PMGfx, tocolor

class PMScreen:
    def __init__(self, width: int = 1920, height: int = 1080):
        self.img = Image.new("I", (width, height), 0)
        self.draw = ImageDraw.Draw(self.img)
        self.gfx = PMGfx()
        self.gfx.width, self.gfx.height = self.img.size
        print(f"Screen size: {self.gfx.width}x{self.gfx.height}")
        print(f"Image size: {self.img.size}")
        self.gfx.x1, self.gfx.y1 = (self.gfx.width-1, self.gfx.height-1)
        self.set_flush(False) ## do not flush by default
        self.clear()

    def set_flush(self, doFlush: bool) -> None:
        self._doFlush = doFlush

    def delay(self, ms: int) -> None:
        time.sleep(ms / 1000)
        if self._doFlush: self.flush()

    def clear(self) -> None:
        self.draw.rectangle(self.gfx.rect, self.gfx.bg_color)
        if self._doFlush: self.flush()

    def line(self, gfx: PMGfx, rect: tuple):
        print(f"Drawing line with rect: {rect} and color: {gfx.color}")
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
        elif fill:
            # Use the specified fill color
            self.draw.ellipse(bbox, outline=gfx.color, width=gfx.line_width, fill=tocolor(fill))
        else:
            # No fill, just draw the outline
            self.draw.ellipse(bbox, outline=gfx.color, width=gfx.line_width)
        if self._doFlush: self.flush()

    def rect(self, gfx: PMGfx, rect: tuple, fill="__use_bg_color__"):
        if fill == "__use_bg_color__":
            # Use the gfx.background color if specified
            self.draw.rectangle(rect, outline=gfx.color, width=gfx.line_width, fill=gfx.bg_color)
        elif fill:
            # Use the specified fill color
            self.draw.rectangle(rect, outline=gfx.color, width=gfx.line_width, fill=tocolor(fill))
        else:
            # No fill, just draw the outline
            self.draw.rectangle(rect, outline=gfx.color, width=gfx.line_width)
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
        ## get text bounding box
        (x_min, y_min, x_max, y_max) = gfx.font.getbbox(msg)
        width = x_max - x_min
        height = y_max

        x0, y0, x1, y1 = rect
        text_x0 = x0
        text_y0 = y0

        if halign == "center": text_x0 = x0 + (x1 - x0 - width) / 2
        elif halign == "left": text_x0 = x0
        elif halign == "right": text_x0 = x1 - width
        else: print(f"Invalid halign '{halign}' in text_box, using 'center' instead.")

        if valign == "center": text_y0 = y0 + (y1 - y0 - height) / 2
        elif valign == "top": text_y0 = y0
        elif valign == "bottom": text_y0 = y1 - height
        else: print(f"Invalid valign '{valign}' in text_box, using 'center' instead.")

        if gfx.text_bg_color: self.draw.rectangle(rect, fill=gfx.text_bg_color)
        self.draw.text((text_x0, text_y0 - y_min), msg, fill=gfx.text_color, font=gfx.font)
        if self._doFlush: self.flush()

    def flush(self):
        raw = self.img.tobytes("raw")
        # Write to framebuffer
        with open("/dev/fb0", "wb") as f:
            f.write(raw[0::2])  # Write every second byte for RGB565 format

    def quit(self):
        if self._doFlush: self.flush()

def main():
    pms = PMScreen(1920, 1080)
    pms.gfx.color = (0, 0, 255)
    pms.clear()
    pms.line(pms.gfx, pms.gfx.rect)
    pms.gfx.color = (255, 0, 0)
    pms.gfx.bg_color = (0, 250, 0)
    pms.rect(pms.gfx, (50, 50, 200, 250)) # red with green inside
    pms.gfx.bg_color = None
    pms.rect(pms.gfx, (100, 100, 250, 300)) # red with clear inside
    pms.rect(pms.gfx, (150, 150, 300, 350), fill=(250, 0, 250)) # red with purple inside
    pms.gfx.text_color = 0xFFFF00  # yello text
    pms.gfx.set_font("NimbusSansNarrow-Oblique", 48)
    pms.text(pms.gfx, "Hello World!", 50,60)
    pms.flush()
    pms.quit()

if __name__ == "__main__":
    main()
