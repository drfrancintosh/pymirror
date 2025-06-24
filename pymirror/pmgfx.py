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
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 255, 255)
        self.text_bg_color = (0, 0, 0)
        self.line_width = 5
        self.font_name = None
        self.font_size = None
        self.font = None 
        self.antialias = True
        self._read_fonts()
    
    def _read_fonts(self):
        if self._fontlist: return # already read fonts
        print("Reading system fonts...")
        self._fontlist = []
        with open("./fontlist.txt", "r") as f:
            fonts = f.read().splitlines()
            for font_path in fonts:
                # split line at # discard the rest
                font_path = font_path.split("#")[0].strip()
                if not font_path: continue # skip empty lines
                # split after the : # discard the rest
                font_path = font_path.split(":")[0].strip()
                if not font_path: continue # skip empty lines
                self._fontlist.append(font_path)

    def set_font(self, font_name, pitch=64):
        if not pitch: pitch = 64
        for font_path in self.fontlist:
            if font_name in font_path:
                self.font = ImageFont.truetype(font_path, size=pitch)
                ## NOTE: we don't set the self.font_name and self.font_size here
                ##       because we want to keep the original font name and size
                # self.font_name = font_name
                # self.font_size = pitch
                return True
        print(f"Font '{font_name}' not found in system fonts. font unchanged.")
        return False

    def reset_font(self):
        ## useful for resetting the font to the default
        return self.set_font(self.font_name, self.font_size)
