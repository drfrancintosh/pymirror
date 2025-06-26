import time
from datetime import datetime
from pymirror.pmmodule import PMModule
from pymirror.pmscreen import PMGfx
import math

def _compute_clock_positions(gfx, dx, dy, r):
	"""Compute the 12 positions around a clock face given center (x0, y0) and radius r."""
	positions = []
	for hour in range(12):
		hrs = str(hour)  # Convert hour to 1-12 format
		(offset, baseline, width, height) = gfx.font.getbbox(hrs)  # Get bounding box of the hour text
		print(hrs, offset, baseline, width, height)
		# Compute the angle for the hour (in radians)
		theta = 2 * math.pi * (hour - 2) / 12 
		x0 = gfx.x0 + dx  # Center x-coordinate
		y0 = gfx.y0 + dy  # Center y-coordinate
		# Calculate x, y using the angle and radius
		x0 = x0 + r * math.cos(theta)  # x-coordinate
		y0 = y0 + r * math.sin(theta)  # y-coordinate
		# Adjust for the font size to center the text
		x0 -= width
		y0 -= height
		x1 = x0 + width
		y1 = y0 + height
		positions.append([hrs, (x0, y0, x1, y1)])

	return positions

def _compute_hand_posn(x0, y0, r, value, divisor, offset):
	value += offset 
	angle = 2 * math.pi * value / divisor 
	return (x0 + r * math.cos(angle), y0 + r * math.sin(angle))

class AnalogClock(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.second_hand = config.second_hand
		self.minute_hand = config.minute_hand
		self.hour_hand = config.hour_hand
		self._render_clock_face()
		self.hour = 0
		self.minute = 0
		self.second = 0
		self.last_hour = -1
		self.last_minute = -1
		self.last_second = -1
		self.hour_length = 0.5
		self.minute_length = 0.66
		self.second_length = 0.75

	def _render_clock_face(self, dx=0, dy=0, r=0):
		"""Render the clock face with hour markers."""
		gfx = self.gfx
		hr = 1
		self.screen.circle(gfx, gfx.x0+dx, gfx.y0+dy, r, fill=gfx.bg_color)
		for posn in _compute_clock_positions(gfx, dx, dy, r):
			hrs, rect = posn
			self.screen.text_box(gfx, hrs, rect, valign="center", halign="center")
			hr += 1
		gfx.line_width = 3

	def render(self, force: bool = False) -> bool:
		save_color = self.gfx.color
		now = datetime.now()
		gfx = self.gfx
		dx = (gfx.x1 - gfx.x0)/2
		dy = (gfx.y1 - gfx.y0)/2
		if dx < dy: r = dx
		else: r = dy

		self._render_clock_face(dx, dy, r)

		if self.hour_hand is not None:
			hr_posn = _compute_hand_posn(gfx.x0+dx, gfx.y0+dy, r*self.hour_length, now.hour + now.minute/60 + now.second/3600, 12.0, -3.0)
			gfx.line_width = 10
			gfx.color = self.hour_hand
			self.screen.line(gfx, (gfx.x0+dx, gfx.y0+dy, hr_posn[0], hr_posn[1]))
			self.last_hour = now.hour

		if self.minute_hand is not None:
			min_posn = _compute_hand_posn(gfx.x0+dx, gfx.y0+dy, r*self.minute_length, now.minute + now.second/60, 60.0, -15.0)
			gfx.line_width = 5
			gfx.color = self.minute_hand
			self.screen.line(gfx, (gfx.x0+dx, gfx.y0+dy, min_posn[0], min_posn[1]))
			self.last_minute = now.minute

		if self.second_hand is not None:
			sec_posn = _compute_hand_posn(gfx.x0+dx, gfx.y0+dy, r*self.second_length, now.second, 60.0, -15.0)
			gfx.line_width = 3
			gfx.color = self.second_hand
			self.screen.line(gfx, (gfx.x0+dx, gfx.y0+dy, sec_posn[0], sec_posn[1]))
			self.last_second = now.second

		self.gfx.color = save_color
		return True

	def exec(self) -> bool:
		now = datetime.now()
		return \
			(self.hour_hand and self.last_hour != now.hour) \
		or (self.minute_hand and self.last_minute != now.minute) \
		or (self.second_hand and self.last_second != now.second)

	def onEvent(self, event):
		pass

