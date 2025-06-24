import subprocess
from PIL import Image, ImageDraw, ImageFont

class PMGfx:
    _fontlist = None

    def __init__(self):
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.width = 1920
        self.height = 1080
        self.color = (255, 255, 255)
        self.bg_color = None # default is transparent
        self.text_color = (255, 255, 255)
        self.text_bg_color = None # default is transparent
        self.line_width = 1
        self.font_name = None
        self.font_size = None
        self.font = None 
        self.antialias = True
        self._read_fonts()
    
    def _read_fonts(self):
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
                self.font_size = pitch
                return True # successfully set the font
        print(f"Font '{font_name}' not found in system fonts. font unchanged.")
        return False