import time
from PIL import Image, ImageDraw
from pymirror.pmgfx import PMGfx

def _image_to_rgb565(img):
    """Convert a Pillow RGB image to raw RGB565 bytes using numpy"""
    # Convert image to RGB (ensure no alpha channel) and then to numpy array
    # img = img.convert("RGB")  # Make sure the image is in RGB mode
    # img_array = np.array(img, dtype=np.uint16)  # Convert to uint16 for correct shifting
    # return img_array
    raw = img.tobytes("raw")
    # Perform the conversion to RGB565 for all pixels at once
    # rgb565_array = ((img_array[..., 0] >> 3) << 11) | \
    #                ((img_array[..., 1] >> 2) << 5) | \
    #                (img_array[..., 2] >> 3)

    # Convert the numpy array to bytes (little-endian)
    # raw = rgb565_array.astype(np.uint16).tobytes()
    return raw

def _color(t):
    # Convert a color tuple (R, G, B) to RGB565 format
    # this is mangled because the PIL Image is a 32-bit signed integer array
    # and we send every other byte to the framebuffer
    # so every pixel (tuple) is converted to a 16-bit RGB565 value
    # split across the odd bytes of a 32-bit integer
    if t is None: return None
    print(f"Converting color {t} to RGB565")
    r, g, b = t
    r = (r >> 3) & 0x1F  # Convert to 5 bits
    g0 = (g >> 2) & 0x07  # Convert to lower 3 bits
    g1 = (g >> 5) & 0x07  # Convert to upper 3 bits
    b = (b >> 3) & 0x1F  # Convert to 5 bits
    x = r << 19 | (g1 << 16 | g0 << 5 | b)
    return x

class PMScreen:
    def __init__(self):
        self.img = Image.new("I", (1920, 1080), 0)
        self.draw = ImageDraw.Draw(self.img)
        self.gfx = PMGfx()
        self.gfx.width, self.gfx.height = self.img.size
        self.gfx.x1, self.gfx.y1 = (self.gfx.width-1, self.gfx.height-1)
        self.set_flush(False)
        self.clear()

    def set_flush(self, doFlush):
        self._doFlush = doFlush
    def delay(self, ms):
        time.sleep(ms / 1000)
        if self._doFlush: self.flush()
    def clear(self):
        self.draw.rectangle((self.gfx.x0, self.gfx.y0, self.gfx.x1, self.gfx.y1), _color(self.gfx.bg_color))
        if self._doFlush: self.flush()
    def line(self, gfx, x0, y0, x1, y1):
        self.draw.line((x0, y0, x1, y1), fill=_color(gfx.color), width=gfx.line_width)
        if self._doFlush: self.flush()
    def ellipse(self, gfx, x0, y0, x1, y1, fill=None):
        if fill:
            self.draw.ellipse((x0, y0, x1, y1), outline=_color(gfx.color), width=gfx.line_width, fill=_color(fill))
        else:
            if gfx.bg_color:
                self.draw.ellipse((x0, y0, x1, y1), outline=_color(gfx.color), width=gfx.line_width, fill=_color(gfx.bg_color))
            else:
                self.draw.ellipse((x0, y0, x1, y1), outline=_color(gfx.color), width=gfx.line_width)
        if self._doFlush: self.flush()
    def circle(self, gfx, x0, y0, r, fill="__use_bg_color__"):
        bbox = (x0-r, y0-r, x0+r, y0+r)
        if fill == "__use_bg_color__":
            # Use the gfx.background color
            self.draw.ellipse(bbox, outline=_color(gfx.color), width=gfx.line_width, fill=_color(gfx.bg_color))
        elif fill:
            # Use the specified fill color
            self.draw.ellipse(bbox, outline=_color(gfx.color), width=gfx.line_width, fill=_color(fill))
        else:
            # No fill, just draw the outline
            self.draw.ellipse(bbox, outline=_color(gfx.color), width=gfx.line_width)
        if self._doFlush: self.flush()
    def rect(self, gfx, x0, y0, x1, y1, fill="__use_bg_color__"):
        if fill == "__use_bg_color__":
            # Use the gfx.background color if specified
            self.draw.rectangle((x0, y0, x1, y1), outline=_color(gfx.color), width=gfx.line_width, fill=_color(gfx.bg_color))
        elif fill:
            # Use the specified fill color
            self.draw.rectangle((x0, y0, x1, y1), outline=_color(gfx.color), width=gfx.line_width, fill=_color(fill))
        else:
            # No fill, just draw the outline
            self.draw.rectangle((x0, y0, x1, y1), outline=_color(gfx.color), width=gfx.line_width)
        if self._doFlush: self.flush()
    def text(self, gfx,  msg, x0, y0):
        (x_min, y_min, x_max, y_max) = gfx.font.getbbox(msg)
        width = x_max - x_min
        height = y_max
        # Draw background rectangle
        if gfx.text_bg_color:
            self.draw.rectangle((x0, y0, x0 + width, y0 + height), fill=_color(gfx.text_bg_color))
        # Draw text
        self.draw.text((x0, y0), msg, fill=_color(gfx.text_color), font=gfx.font)
        if self._doFlush: self.flush()
    def text_box(self, gfx, msg, x0=None, y0=None, x1=None, y1=None, valign="center", halign="center"):
        ## get text bounding box
        (x_min, y_min, x_max, y_max) = gfx.font.getbbox(msg)
        width = x_max - x_min
        height = y_max

        ## if x0, y0 not specified, use the gfx.x0, y0
        ## if they are specified, then they are absolute coordinates
        if x0 == None: x0 = gfx.x0
        if y0 == None: y0 = gfx.y0

        text_x0 = x0
        text_y0 = y0

        ## if x1, y1 not specified, use the gfx.x1, y1
        ## if they are specified, then they are absolute coordinates
        if x1 == None: x1 = gfx.x1
        if y1 == None: y1 = gfx.y1

        if halign == "center": text_x0 = x0 + (x1 - x0 - width) / 2
        elif halign == "left": text_x0 = x0
        elif halign == "right": text_x0 = x1 - width
        else: print(f"Invalid halign '{halign}' in text_box, using 'center' instead.")

        if valign == "center": text_y0 = y0 + (y1 - y0 - height) / 2
        elif valign == "top": text_y0 = y0
        elif valign == "bottom": text_y0 = y1 - height
        else: print(f"Invalid valign '{valign}' in text_box, using 'center' instead.")

        if gfx.text_bg_color: self.draw.rectangle((x0, y0, x1, y1), fill=_color(gfx.text_bg_color))
        self.draw.text((text_x0, text_y0), msg, fill=_color(gfx.text_color), font=gfx.font)
        if self._doFlush: self.flush()

    def flush(self):
        raw = self.img.tobytes("raw")
        # Write to framebuffer
        with open("/dev/fb0", "wb") as f:
            f.write(raw[0::2])  # Write every second byte for RGB565 format

    def quit(self):
        if self._doFlush: self.flush()

def main():
    pms = PMScreen()
    pms.gfx.color = (0, 0, 255)
    pms.line(pms.gfx, 0,0,pms.gfx.width, pms.gfx.height)
    pms.gfx.color = (255, 0, 0)
    pms.gfx.text_color = (0, 255, 0)
    pms.gfx.set_font("NimbusSansNarrow-Oblique", 48)
    pms.text(pms.gfx, "Hello World!", 50,60)
    pms.gfx.bg_color = (0, 250, 0)
    pms.rect(pms.gfx, 50, 50, 200, 250) # red with green inside
    pms.gfx.bg_color = None
    pms.rect(pms.gfx, 100, 100, 250, 300) # red with clear inside
    pms.rect(pms.gfx, 150, 150, 300, 350, fill=(250, 0, 250)) # red with purple inside
    pms.flush()
    time.sleep(3)
    pms.quit()

if __name__ == "__main__":
    main()
