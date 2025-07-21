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
			self.image = self.load(self._image.path)
			if self._slideshow.frame and not self.frame_img:
				img = PILImage.open(self._image.path)
				img = self.image.scale(img, self.gfx.width, self.gfx.height, self._slideshow.scale).convert("RGBA")
				frame_img = PILImage.open(self._slideshow.frame)
				self.frame_img = self.image.scale(frame_img, self.gfx.width, self.gfx.height, "stretch").convert("RGBA")
			if self.frame_img:
				img.paste(self.frame_img, (0, 0), self.frame_img)
				img = self.image.convert_internal(img)
				self.image.set_img(img)
			self.dirty = True
		return self.dirty

