from abc import ABC, abstractmethod
import copy
from pymirror.pmscreen import PMGfx
from dataclasses import dataclass

from pymirror.pmtimer import PMTimer
from pymirror.utils import SafeNamespace

@dataclass
class PMModuleDef(ABC):
	name: str = None
	position: str = "None"
	color: str = "#fff"
	bg_color: str = None
	text_color: str = "#fff"
	text_bg_color: str = None
	font: str = "DejaVuSans.ttf"
	font_size: int = 64
	subscriptions: list[str] = None
	disabled: bool = False

class PMModule(ABC):
	def __init__(self, pm, config: SafeNamespace):
		self.pm = pm
		self.screen = pm.screen
		self.moddef = PMModuleDef(**config.moddef.__dict__) if config.moddef else PMModuleDef(name=self.__class__.__name__, position="None")
		if not self.moddef.name: self.moddef.name = self.__class__.__name__
		self.config = config
		self.timer = PMTimer(0)
		self.subscriptions = []
		self.gfx = PMGfx() ## default graphics context
		self.gfx.color = self.moddef.color or self.screen.gfx.color
		self.gfx.bg_color = self.moddef.bg_color or self.screen.gfx.bg_color
		self.gfx.text_color = self.moddef.text_color or self.screen.gfx.text_color
		self.gfx.text_bg_color = self.moddef.text_bg_color or self.screen.gfx.text_bg_color
		self.gfx.font_name = self.moddef.font or self.screen.gfx.font_name or "DejaVuSans.ttf"
		self.gfx.font_size = self.moddef.font_size or 64
		self.gfx.set_font(self.gfx.font_name, self.gfx.font_size)
		self.subscribe(self.moddef.subscriptions or [])
		if self.moddef.position:
			dim_str = pm.config.positions[self.moddef.position]
			dims = [float(x) for x in dim_str.split(",")]
			## this is the bounding box for the module
			## x0, y0 is the top-left corner, x1, y1 is the bottom-right corner
			## these are in percentages of the screen size
			## so we need to multiply to get the actual pixel values
			self.gfx.rect = (
				int((self.pm.screen.gfx.width - 1) * dims[0]),
				int((self.pm.screen.gfx.height - 1) * dims[1]),
				int((self.pm.screen.gfx.width - 1) * dims[2]),
				int((self.pm.screen.gfx.height - 1) * dims[3])
			)


	def subscribe(self, event_names):
		if isinstance(event_names, str):
			event_names = [event_names]
		for event_name in event_names:
			self.subscriptions.append(event_name)

	def is_subscribed(self, event_name):
		return event_name in self.subscriptions

	def clear_region(self) -> None:
		""" Clear the module's region on the screen. """
		gfx = copy.copy(self.gfx)
		gfx.color = gfx.bg_color
		self.screen.rect(gfx, gfx.rect, fill=gfx.bg_color)

	def dispatchEvent(self, event) -> None:
		method_name = f"on{event.event}"
		method = getattr(self, method_name, None)
		if method:
			method(event)
		else:
			print(f"No handler for event {event.name} in module {self.moddef.position}")

	@abstractmethod
	def render(self, force: bool = False) -> bool:
		""" Render the module on the screen.
		returns True if the screen was updated, and needs a flush() call.
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
		print(f"onEvent {self.moddef.name} received event: {event.event}")
		self.dispatchEvent(event)
