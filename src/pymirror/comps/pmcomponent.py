from abc import ABC
from dataclasses import dataclass, fields

from pmgfxlib.pmgfx import PMGfx
from pymirror.utils import SafeNamespace, from_dict
from pymirror.pmconstants import PMConstants as PMC
from pmgfxlib.pmbitmap import PMBitmap
from pymirror.pmrect import PMRect

class PMComponent(ABC):
	def __init__(self, config: SafeNamespace):
		self._config = config
		self.gfx = PMGfx.from_dict(config.__dict__)

	@property
	def width(self) -> PMRect:
		return self.gfx.width

	@property
	def height(self) -> PMRect:
		return self.gfx.height

	@width.setter
	def width(self, value: int) -> None:
		self.gfx.width = value

	@height.setter
	def height(self, value: int) -> None:
		self.gfx.height = value

	def render(self, bitmap: PMBitmap) -> None:
		"""Render the component to its bitmap."""
		raise NotImplementedError("Subclasses must implement render method")

	def is_dirty(self) -> bool:
		"""Check if the component is dirty (i.e., needs to be re-rendered)."""
		raise NotImplementedError("Subclasses must implement is_dirty method")

	def clean(self) -> bool:
		"""make the component clean"""
		raise NotImplementedError("Subclasses must implement clean method")

	def update(self, msg: str) -> bool:
		"""Update the component with a new message."""
		raise NotImplementedError("Subclasses must implement update method")

if __name__ == "__main__":
	# Example usage
	config = SafeNamespace(rect=(0, 0, 100, 100), color="#fff", bg_color="#000", other_attr="example")
	component = PMComponent(config)
	print(f"Component created with rect: {component._config.rect}, color: {component._config.color}")
	# Note: Actual rendering logic would be implemented in subclasses.