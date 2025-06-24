import subprocess
from PIL import Image, ImageDraw, ImageFont

FONT_LIST=[font_name.split(":")[0] for font_name in subprocess.check_output(["fc-list"], text=True).split("\n")]

class PMGfx:
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
		self.font = ImageFont.truetype("arial.ttf", 24)  # Default font if none is set
		self.antialias = True
	
	def set_font(self, font_name, pitch=24):
		if not pitch: pitch = 24
		for font_path in FONT_LIST:
			if font_name in font_path:
				self.font = ImageFont.truetype(font_path, size=pitch)
				return True
		print(f"Font '{font_name}' not found in system fonts. font unchanged.")
		return False
