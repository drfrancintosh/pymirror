from modules.image import Image
from pymirror.pmmodule import PMModule
from pymirror.pmtimer import PMTimer
from pymirror.utils import SafeNamespace
from pymirror.pmimage import PMImage
import os

class Slideshow(Image):
	def __init__(self, pm, config: SafeNamespace):
		super().__init__(pm, config)
		self._image = config.slideshow ## very cheap way to reuse the Image module
		self._slideshow = config.slideshow
		self.folder = self._slideshow.folder
		self.images = self.load_folder(self.folder)
		self.timer = PMTimer(1)
		self.image_number = 0
		self.dirty = False

	def load_folder(self, folder: str):
		""" Load all images from the given folder """
		self.images = []
		for image_path in os.listdir(folder):
			self.images.append(image_path)
		print(f"Loaded {len(self.images)} images from {folder}")
		return self.images
	
	def exec(self):
		if self.timer.is_timedout():
			if self.images:
				self.timer.set_timeout(self._slideshow.interval_secs * 1000)  # Convert seconds to milliseconds
				self._image.path = os.path.join(self.folder, self.images[self.image_number])
				self.image = self.load(self._image.path)
				self.image_number = (self.image_number + 1) % len(self.images)
				self.dirty = True
		return self.dirty

