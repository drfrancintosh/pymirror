from abc import ABC
from dataclasses import dataclass, fields

from pmgfxlib.pmgfx import PMGfx
from pymirror.utils import SafeNamespace
from pymirror.pmconstants import PMConstants as PMC
from pmgfxlib.pmbitmap import PMBitmap
from pymirror.pmrect import PMRect

@dataclass
class PMComponentConfig:
	rect: PMRect = PMRect(0, 0, 0, 0)
	color: str = PMC.color
	bg_color: str = PMC.bg_color
	text_color: str = PMC.text_color
	text_bg_color: str = PMC.text_bg_color
	font_name: str = PMC.font_name
	font_size: int = PMC.font_size

	@classmethod
	def from_dict(cls, config_dict: dict):
		"""Create PMComponentConfig from dict, ignoring extra keys"""
		# Get only the fields that exist in the dataclass
		valid_fields = {f.name for f in fields(cls)}
		filtered_dict = {k: v for k, v in config_dict.items() if k in valid_fields}
		return cls(**filtered_dict)

@dataclass	
class PMComponent(ABC):
	def __init__(self, config: SafeNamespace):
		self._config = PMComponentConfig.from_dict(config.__dict__)
		self.gfx = gfx = PMGfx()
		gfx.color = self._config.color
		gfx.bg_color = self._config.bg_color
		gfx.text_color = self._config.text_color
		gfx.text_bg_color = self._config.text_bg_color
		gfx.font.set_font(self._config.font_name, self._config.font_size)

	def render(self, bitmap: PMBitmap) -> None:
		"""Render the component to its bitmap."""
		raise NotImplementedError("Subclasses must implement render method")

if __name__ == "__main__":
	# Example usage
	config = SafeNamespace(rect=(0, 0, 100, 100), color="#fff", bg_color="#000", other_attr="example")
	component = PMComponent(config)
	print(f"Component created with rect: {component._config.rect}, color: {component._config.color}")
	# Note: Actual rendering logic would be implemented in subclasses.