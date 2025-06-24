import time
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pymirror.pmgfx import PMGfx

def _image_to_rgb565(img):
    """Convert a Pillow RGB image to raw RGB565 bytes using numpy"""
    # Convert image to RGB (ensure no alpha channel) and then to numpy array
    img = img.convert("RGB")  # Make sure the image is in RGB mode
    img_array = np.array(img, dtype=np.uint16)  # Convert to uint16 for correct shifting

    # Perform the conversion to RGB565 for all pixels at once
    rgb565_array = ((img_array[..., 0] >> 3) << 11) | \
                   ((img_array[..., 1] >> 2) << 5) | \
                   (img_array[..., 2] >> 3)

    # Convert the numpy array to bytes (little-endian)
    raw = rgb565_array.astype(np.uint16).tobytes()
    return raw


class PMScreen:
	def __init__(self):
		self.img = Image.new("RGB", (1920, 1080), (0, 0, 0))
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
		self.draw.rectangle((self.gfx.x0, self.gfx.y0, self.gfx.x1, self.gfx.y1), self.gfx.bg_color)
		if self._doFlush: self.flush()
	def line(self, gfx, x0, y0, x1, y1):
		self.draw.line((x0, y0, x1, y1), fill=gfx.color, width=gfx.line_width)
		if self._doFlush: self.flush()
	def ellipse(self, gfx, x0, y0, x1, y1, fill=None):
		if fill:
			self.draw.ellipse((x0, y0, x1, y1), outline=gfx.color, width=gfx.line_width, fill=fill)
		else:
			if gfx.bg_color:
				self.draw.ellipse((x0, y0, x1, y1), outline=gfx.color, width=gfx.line_width, fill=gfx.bg_color)
			else:
				self.draw.ellipse((x0, y0, x1, y1), outline=gfx.color, width=gfx.line_width)
		if self._doFlush: self.flush()
	def circle(self, gfx, x0, y0, r, fill=None):
		bbox = (x0-r, y0-r, x0+r, y0+r)
		if fill:
			self.draw.ellipse(bbox, outline=gfx.color, width=gfx.line_width, fill=fill)
		else:
			if gfx.bg_color:
				self.draw.ellipse(bbox, outline=gfx.color, width=gfx.line_width, fill=gfx.bg_color)
			else:
				self.draw.ellipse(bbox, outline=gfx.color, width=gfx.line_width)
		if self._doFlush: self.flush()
	def rect(self, gfx, x0, y0, x1, y1, fill=None):
		if fill:
			self.draw.rectangle((x0, y0, x1, y1), outline=gfx.color, width=gfx.line_width, fill=fill)
		else:
			if gfx.bg_color:
				self.draw.rectangle((x0, y0, x1, y1), outline=gfx.color, width=gfx.line_width, fill=gfx.bg_color)
			else:
				self.draw.rectangle((x0, y0, x1, y1), outline=gfx.color, width=gfx.line_width)
		if self._doFlush: self.flush()
	def text(self, gfx,  msg, x0, y0):
		self.draw.text((x0, y0), msg, fill=gfx.text_color, font=gfx.font)
		if self._doFlush: self.flush()
	def text_box(self, gfx, msg, x0, y0, x1=None, y1=None, halign="center", valign="center"):
		bbox = gfx.font.getbbox(msg)
		width = bbox[2] - bbox[0]
		height = bbox[3] - bbox[1]
		if x1 == None: x1 = x0 + width
		if y1 == None: y1 = y0 + height
		if x1 < 0: x1 += self.gfx.width
		if y1 < 0: y1 += self.gfx.height

		if halign == "left": x0 = x0
		elif halign == "center": x0 += (x1 - x0 - width) / 2
		elif halign == "right": x0 = x1 - width
		else: print(f"Invalid halign '{halign}' in text_box, using 'center' instead.")

		if valign == "top": y0 = y0
		elif valign == "center": y0 += (y1 - y0 - height) / 2
		elif valign == "bottom": y0 = y1 - height
		else: print(f"Invalid valign '{valign}' in text_box, using 'center' instead.")
		
		if gfx.text_bg_color: self.draw.rectangle((x0, y0, x1, y1), fill=gfx.text_bg_color)
		self.draw.text((x0, y0), msg, fill=gfx.text_color, font=gfx.font)
		if self._doFlush: self.flush()

	def flush(self):
		raw = _image_to_rgb565(self.img)
		# Write to framebuffer
		with open("/dev/fb0", "wb") as f:
			f.write(raw)

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
