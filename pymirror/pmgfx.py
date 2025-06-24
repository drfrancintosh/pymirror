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
        self.antialias = True
        self.set_font("DejaVuSerif", 64)  # default font
        self._read_fonts()

    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, value):
        self._color = _color_to_int(value)

    @property
    def bg_color(self):
        return self._bg_color
    @bg_color.setter
    def bg_color(self, value):
        self._bg_color = _color_to_int(value)

    @property
    def text_color(self):
        return self._text_color
    @text_color.setter
    def text_color(self, value):
        self._text_color = _color_to_int(value)

    @property
    def text_bg_color(self):
        return self._text_bg_color
    @text_bg_color.setter
    def text_bg_color(self, value):
        self._text_bg_color = _color_to_int(value)

    def _read_fonts(self) -> None:
        if self.__class__._fontlist: return # already read fonts
        self.__class__._fontlist = []
        with open("./fontlist.txt", "r") as f:
            fonts = f.read().splitlines()
            for font_path in fonts:
                print(f"Found font: {font_path}")
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
                self.font_size = pitch
                return True # successfully set the font
        print(f"Font '{font_name}' not found in system fonts. font unchanged.")
        return False
    
def _color_to_int(t):
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
                t = tuple(int(t[i:i+2], 16) for i in (0, 2, 4))
            elif t.startswith("(") and t.endswith(")"):
                # Convert rgb() string to RGB tuple
                t = t[1:-1].split(',')
                t = [int(x.strip()) for x in t]
                if len(t) < 3:
                    raise ValueError(f"Invalid rgb() format, expected (R, G, B).")
            return _color(tuple(t))  # Recursively convert to tuple if it's a string
        r, g, b = t
        r = (r >> 3) & 0x1F  # Convert to 5 bits
        g0 = (g >> 2) & 0x07  # Convert to lower 3 bits
        g1 = (g >> 5) & 0x07  # Convert to upper 3 bits
        b = (b >> 3) & 0x1F  # Convert to 5 bits
        x = r << 19 | (g1 << 16 | g0 << 5 | b)
        return x
    except Exception as e:
        raise ValueError(f"Invalid color format {t}, expected RGB tuple or hex string.") from e

