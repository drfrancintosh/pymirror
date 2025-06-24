import subprocess
from PIL import Image, ImageDraw, ImageFont

FONT_LIST=[font_name.split(":")[0] for font_name in subprocess.check_output(["fc-list"], text=True).split("\n")]

class PMGfx:
    fontlist = None

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
    
    def _read_fonts(self):
        """Read the system fonts and return a list of font names."""
        try:
            return [font_name.split(":")[0] for font_name in subprocess.check_output(["fc-list"], text=True).split("\n") if font_name.strip()]
        except subprocess.CalledProcessError as e:
            print(f"Error reading system fonts: {e}")
            return []
    def set_font(self, font_name, pitch=64):
        if not pitch: pitch = 64
        for font_path in FONT_LIST:
            if font_name in font_path:
                self.font = ImageFont.truetype(font_path, size=pitch)
                ## NOTE: we don't set the font_name and font_size here
                ##       because we want to keep the original font name and size
                # self.font_name = font_name
                # self.font_size = pitch
                return True
        print(f"Font '{font_name}' not found in system fonts. font unchanged.")
        return False

    def reset_font(self):
        ## useful for resetting the font to the default
        return self.set_font(self.font_name, self.font_size)
