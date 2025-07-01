from abc import ABC, abstractmethod
import copy
from dataclasses import dataclass

from pymirror.pmbitmap import PMBitmap
from pymirror.pmtimer import PMTimer
from pymirror.pmgfx import PMGfx
from pymirror.utils import SafeNamespace

@dataclass
class PMModuleDef(ABC):
	name: str = None
	position: str = "None"
	color: str = "#fff"
	bg_color: str = None
	text_color: str = "#fff"
	text_bg_color: str = None
	font_name: str = "DejaVuSans.ttf"
	font_size: int = 64
	subscriptions: list[str] = None
	disabled: bool = False
	force_render: bool = False

class PMModule(ABC):
	def __init__(self, pm, config: SafeNamespace):
		self._config = config
		# GLS - need to remove this dependency on pm
		self.pm = pm
		self._moddef = _moddef = PMModuleDef(**config.moddef.__dict__) if config.moddef else PMModuleDef(name=self.__class__.__name__, position="None")
		self.screen = pm.screen
		self.name = _moddef.name or self.__class__.__name__
		self.position = _moddef.position
		self.disabled = _moddef.disabled
		self.timer = PMTimer(0)
		self.subscriptions = []
		self.gfx = PMGfx() ## default graphics context
		self.gfx.rect = self._compute_rect()
		self.gfx.color = _moddef.color or self.screen.gfx.color or self.gfx.color
		self.gfx.bg_color = _moddef.bg_color or self.screen.gfx.bg_color or self.gfx.bg_color
		self.gfx.text_color = _moddef.text_color or self.screen.gfx.text_color or self.gfx.text_color
		self.gfx.text_bg_color = _moddef.text_bg_color or self.screen.gfx.text_bg_color or self.gfx.text_bg_color
		self.gfx.font_name = _moddef.font_name or self.screen.gfx.font_name or self.gfx.font_name
		self.gfx.font_size = _moddef.font_size or self.screen.gfx.font_size or self.gfx.font_size
		self.gfx.set_font(self.gfx.font_name, self.gfx.font_size)
		self.bitmap = self._allocate_bitmap()
		self.subscribe(_moddef.subscriptions or [])

	def _compute_rect(self) -> tuple:
		# compute rect based on "position"
		moddef = self._moddef
		rect = (0,0,0,0)
		if not moddef.position or moddef.position == "None": return None
		dim_str = self.pm._config.positions[moddef.position]
		if dim_str:
			print(f"Module {self._moddef.name} position: {moddef.position}, dimensions: {dim_str}")
			dims = [float(x) for x in dim_str.split(",")]
			## this is the bounding box for the module on-screen
			## x0, y0 is the top-left corner, x1, y1 is the bottom-right corner
			## these are in percentages of the screen size
			## so we need to multiply to get the actual pixel values
			rect = (
				int((self.pm.screen.gfx.width) * dims[0]),
				int((self.pm.screen.gfx.height) * dims[1]),
				int((self.pm.screen.gfx.width) * dims[2]),
				int((self.pm.screen.gfx.height) * dims[3])
			)
		return rect
	
	def _allocate_bitmap(self):
		if not self.gfx.rect:
			print(f"Module {self._moddef.name} has no rect defined, cannot allocate bitmap.")
			return None
		width = self.gfx.x1 - self.gfx.x0 + 1
		height = self.gfx.y1 - self.gfx.y0 + 1
		return PMBitmap(width, height, self.gfx.bg_color)

	@abstractmethod
	def render(self, force: bool = False) -> bool:
		""" Render the module on its bitmap.
		returns True if the bitmap was updated, and needs a flush() call.
		If force is True, the module should always render, even if nothing changed.
		"""
		pass

	@abstractmethod
	def exec(self) -> bool:
		""" Execute the module logic.
		returns True if the module state changed, and needs a render() call.
		"""
		pass

	def onEvent(self, event) -> None:
		""" Handle an event.
		This is called by the PM when an event is dispatched to the module.
		Override this method to handle specific events.
		"""
		print(f"onEvent {self._moddef.name} received event: {event.event}")
		self.dispatchEvent(event)

	def subscribe(self, event_names):
		if isinstance(event_names, str):
			event_names = [event_names]
		for event_name in event_names:
			self.subscriptions.append(event_name)

	def is_subscribed(self, event_name):
		return event_name in self.subscriptions

	def dispatchEvent(self, event) -> None:
		method_name = f"on{event.event}"
		method = getattr(self, method_name, None)
		if method:
			method(event)
		else:
			print(f"No handler for event {event.name} in module {self._moddef.position}")
