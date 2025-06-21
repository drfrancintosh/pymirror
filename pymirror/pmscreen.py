import os 
import time

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
		self.font = None
		self.antialias = True
		
class PMScreen:
	def __init__(self):
		os.putenv("SDL_AUDIODRIVER", "dummy")
		os.putenv("SDL_FBDEV", "/dev/fb0")
		os.putenv("SDL_VIDEODRIVER", "fbcon")
		import pygame
		self.pygame = pygame

		# Initialize self.pygame and hide the mouse
		self.pygame.init()
		self.screen = self.pygame.display.set_mode((0, 0), self.pygame.FULLSCREEN)
		self.pygame.mouse.set_visible(False)
		self.gfx = PMGfx()
		self.gfx.width, self.gfx.height = self.screen.get_size()
		self.gfx.x1, self.gfx.y1 = (self.gfx.width-1, self.gfx.height-1)
		self.gfx.font = self.pygame.font.Font(None, 64)
		self.set_flush(False)
		self.info = self.pygame.display.Info()
		self.buffer = self.pygame.Surface((self.gfx.width, self.gfx.height))
		self.clear()

	def set_flush(self, doFlush):
		self._doFlush = doFlush
	def delay(self, ms):
		self.pygame.time.delay(ms)
		if self._doFlush: self.flush()
	def clear(self):
		self.buffer.fill(self.gfx.bg_color)
		if self._doFlush: self.flush()
	def line(self, gfx, x0, y0, x1, y1):
		self.pygame.draw.line(self.buffer, gfx.color, (x0,y0), (x1,y1), gfx.line_width)
		if self._doFlush: self.flush()
	def rect(self, gfx, x0, y0, x1, y1):
		self.pygame.draw.rect(self.buffer, gfx.color, (x0, y0, x1, y1))
		if self._doFlush: self.flush()
	def box(self, gfx, x0, y0, x1, y1):
		self.pygame.draw.rect(self.buffer, gfx.color, (x0, y0, x1, y1), gfx.line_width)
		if self._doFlush: self.flush()
	def text(self, gfx,  msg, x0, y0):
		text = (gfx.font or self.gfx.font).render(msg, gfx.antialias, gfx.text_color, gfx.text_bg_color)
		self.buffer.blit(text, (x0, y0))
		if self._doFlush: self.flush()
	def text_box(self, gfx, msg, x0, y0, x1=None, y1=None, halign="center", valign="center"):
		width, height = (gfx.font or self.gfx.font).size(msg)
		if x1 == None: x1 = x0 + width
		if y1 == None: y1 = y0 + height
		if x1 < 0: x1 += self.gfx.width
		if y1 < 0: y1 += self.gfx.height
		if halign == "left": x0 = x0
		if halign == "center": x0 += (x1 - x0 - width) / 2
		if halign == "right": x0 = x1 - width
		if valign == "top": y0 = y0
		if valign == "center": y0 += (y1 - y0 - height) / 2
		if valign == "bottom": y0 = y1 - height
		if gfx.text_bg_color: self.pygame.draw.rect(self.buffer, gfx.text_bg_color, (x0, y0, x1, y1))
		text = (gfx.font or self.gfx.font).render(msg, gfx.antialias, gfx.text_color, gfx.text_bg_color)
		self.buffer.blit(text, (x0, y0))
		if self._doFlush: self.flush()

	def flush(self):
		self.screen.blit(self.buffer, (0, 0))
		self.pygame.display.flip()	
	def quit(self):
		if self._doFlush: self.flush()
		self.pygame.quit()

def main():
	pms = PMScreen()
	pms.line(pms.gfx, 0,0,pms.gfx.width, pms.gfx.height)
	pms.rect(pms.gfx, 50, 50, 100, 150)
	pms.text(pms.gfx, "Hello World!", 50,60)
	pms.flush()
	time.sleep(3)
	pms.quit()

if __name__ == "__main__":
	main()
