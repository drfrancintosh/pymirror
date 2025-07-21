from pymirror.pmmodule import PMModule
from pymirror.utils import SafeNamespace
from pymirror.pmimage import PMImage

class Image(PMModule):
	def __init__(self, pm, config: SafeNamespace):
		super().__init__(pm, config)
		if config.image:
			self._image = config.image
			self.image = self.load(self._image.path)
			self.dirty = True

	def load(self, path: str):
		""" Load an image from the given path """
		self.image = PMImage(path, self.gfx.width, self.gfx.height, self._image.scale)
		self.dirty = True
		return self.image
	
	def render(self, force: bool = False) -> bool:
		self.bitmap.clear()
		## scale the image to fit the bitmap
		x0 = 0
		y0 = 0
		if self._image.valign == "top":
			y0 = 0
		elif self._image.valign == "bottom":
			y0 = self.gfx.height - self.image.img.height
		elif self._image.valign == "center":
			y0 = (self.gfx.height - self.image.img.height) // 2
		if self._image.halign == "left":
			x0 = 0
		elif self._image.halign == "right":
			x0 = self.gfx.width - self.image.img.width
		elif self._image.halign == "center":
			x0 = (self.gfx.width - self.image.img.width) // 2
		self.image_rect = (x0, y0, x0 + self.image.img.width, y0 + self.image.img.height)
		self.bitmap.img.paste(self.image.img, (x0, y0))
		self.dirty = False
		return True

	def exec(self):
		return self.dirty

