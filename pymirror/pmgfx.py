from PIL import ImageFont

class PMGfx:
    _fontlist = None

    def __init__(self):
        self.rect = (0,0,0,0)  # x0, y0, x1, y1
        self.width = 0
        self.height = 0
        self._color = "#ffffff"  # default white color
        self._bg_color = None # default is transparent
        self._text_color = "#ffffff"  # default white text color
        self._text_bg_color = None # default is transparent
        self.line_width = 1
        self.font_name = None
        self.font_size = None
        self.font = None
        self.font_height = 0
        self.font_width = 0
        self.antialias = True
        self._read_fonts()
        self.set_font("DejaVuSerif", 64)  # default font

    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, value):
        self._color = tocolor(value)

    @property
    def bg_color(self):
        return self._bg_color
    @bg_color.setter
    def bg_color(self, value):
        self._bg_color = tocolor(value)

    @property
    def text_color(self):
        return self._text_color
    @text_color.setter
    def text_color(self, value):
        self._text_color = tocolor(value)

    @property
    def text_bg_color(self):
        return self._text_bg_color
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

    def _read_fonts(self) -> None:
        if self.__class__._fontlist: return # already read fonts
        self.__class__._fontlist = []
        with open("./fontlist.txt", "r") as f:
            fonts = f.read().splitlines()
            for font_path in fonts:
                # split line at # discard the rest
                font_path = font_path.split("#")[0].strip()
                if not font_path: continue # skip empty lines
                # split after the : # discard the rest
                font_path = font_path.split(":")[0].strip()
                if not font_path: continue # skip empty lines
                self.__class__._fontlist.append(font_path)

    def set_font(self, font_name: str, pitch: int = 64) -> bool:
        if not pitch: pitch = 64
        for font_path in self.__class__._fontlist:
            if font_name in font_path:
                self.font = ImageFont.truetype(font_path, size=pitch)
                self.font_name = font_name
                self.font_size = int(pitch)
                self.font_metrics = self.font.getbbox("M")
                self.font_offset = self.font_metrics[0]
                self.font_baseline = self.font_metrics[1]
                self.font_width = self.font_metrics[2]
                self.font_height = self.font_metrics[3]
                return True # successfully set the font
        print(f"Font '{font_name}' not found in system fonts. font unchanged.")
        return False
    
def tocolor(t):
    # Convert a color tuple (R, G, B) to RGB565 format
    # this is mangled because the PIL Image is a 32-bit signed integer array
    # and we send every other byte to the framebuffer
    # so every pixel (tuple) is converted to a 16-bit RGB565 value
    # split across the odd bytes of a 32-bit integer
    try:
        if t is None: return None
        if isinstance(t, int): return t  # Already an integer
        if isinstance(t, str):
            if t.startswith("#"):
                # Convert hex color to RGB tuple
                t = t.lstrip("#")
                if len(t) == 3:
                    s = t
                    t = tuple(int(t[i]* 16, 16) for i in (0, 1, 2))
                    print(f"Converting 3-digit hex color {s} to RGB tuple {t}")
                elif len(t) == 6:
                    t = tuple(int(t[i:i+2], 16) for i in (0, 2, 4))
                else:
                    raise ValueError(f"Invalid hex color format {t}, expected 3 or 6 hex digits.")
            elif t.startswith("(") and t.endswith(")"):
                # Convert rgb() string to RGB tuple
                t = t[1:-1].split(',')
                t = [int(x.strip()) for x in t]
                if len(t) < 3:
                    raise ValueError(f"Invalid rgb() format, expected (R, G, B).")
            return tocolor(tuple(t))  # Recursively convert to tuple if it's a string
        r, g, b = t
        r = (r >> 3) & 0x1F  # Convert to 5 bits
        g0 = (g >> 2) & 0x07  # Convert to lower 3 bits
        g1 = (g >> 5) & 0x07  # Convert to upper 3 bits
        b = (b >> 3) & 0x1F  # Convert to 5 bits
        x = r << 19 | (g1 << 16 | g0 << 5 | b)
        return x
    except Exception as e:
        raise ValueError(f"Invalid color format {t}, expected RGB tuple or hex string.") from e

