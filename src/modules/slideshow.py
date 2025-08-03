from random import random, randint, choice  # Import the functions you need
from modules.image import Image
from pymirror.pmmodule import PMModule
from pymirror.pmtimer import PMTimer
from pymirror.utils import SafeNamespace
from pymirror.pmimage import PMImage
import os
from PIL import Image as PILImage

class Slideshow(Image):
	def __init__(self, pm, config: SafeNamespace):
		super().__init__(pm, config)
		self._image = config.slideshow ## very cheap way to reuse the Image module
		self._slideshow = config.slideshow
		self.randomize = self._slideshow.randomize
		self.folder = self._slideshow.folder
		self.images = self.load_folder(self.folder)
		self.timer = PMTimer(1)
		self.image_number = 0
		self.dirty = False
		self.frame_img = None

	def load_folder(self, folder: str):
		""" Load all images from the given folder """
		self.images = []
		for image_path in os.listdir(folder):
			self.images.append(image_path)
		print(f"Loaded {len(self.images)} images from {folder}")
		return self.images

	def exec(self):
		if self.timer.is_timedout():
			self.timer.set_timeout(self._slideshow.interval_secs * 1000)  # Convert seconds to milliseconds
			if self.randomize:
				self.image_number = randint(0, len(self.images) - 1)
			else:
				self.image_number = (self.image_number + 1) % len(self.images)
			self._image.path = os.path.join(self.folder, self.images[self.image_number])
			if self._slideshow.frame:
				if not self.frame_img:
					self.image = PMImage(None, SafeNamespace())
					img = PILImage.open(self._image.path)
					img = self.image.scale(img, self.bitmap.gfx.width, self.bitmap.gfx.height, self._slideshow.scale).convert("RGBA")
					frame_img = PILImage.open(self._slideshow.frame)
					frame_img = self.image.scale(frame_img, self.bitmap.gfx.width, self.bitmap.gfx.height, "stretch").convert("RGBA")
					self.frame_img = frame_img
					img.paste(self.frame_img, (0, 0), self.frame_img)
					self.image.img = img
				else:
					self.image = PMImage(None, SafeNamespace())
					img = PILImage.open(self._image.path)
					img = self.image.scale(img, self.bitmap.gfx.width, self.bitmap.gfx.height, self._slideshow.scale).convert("RGBA")
					img.paste(self.frame_img, (0, 0), self.frame_img)
					self.image.img = img
			else:
				self.image = self.load(self._image.path)
			self.dirty = True
		return self.dirty

