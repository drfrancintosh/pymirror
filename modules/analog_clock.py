import time
from datetime import datetime
from pymirror.pmmodule import PMModule
from pymirror.pmscreen import PMGfx
import math

def _compute_clock_positions(x0, y0, r):
    """Compute the 12 positions around a clock face given center (x0, y0) and radius r."""
    positions = []
    for hour in range(12):
        # Compute the angle for the hour (in radians)
        theta = 2 * math.pi * (hour - 2) / 12 
        
        # Calculate x, y using the angle and radius
        x = x0 + r * math.cos(theta)  # x-coordinate
        y = y0 + r * math.sin(theta)  # y-coordinate
        
        # Append the position as a tuple (x, y)
        positions.append((x, y))
    
    return positions

def _compute_hand_posn(x0, y0, r, value, divisor, offset):
	value += offset 
	angle = 2 * math.pi * value / divisor 
	return (x0 + r * math.cos(angle), y0 + r * math.sin(angle))

class AnalogClock(PMModule):
	def __init__(self, pm, moddef, config):
		super().__init__(pm, moddef, config)
		self.second_hand = config.second_hand
		self.minute_hand = config.minute_hand or (self.gfx.color)
		self.hour_hand = config.hour_hand or self.gfx.color
		self.render_clock_face()
		self.hour = 0
		self.minute = 0
		self.second = 0
		self.last_hour = -1
		self.last_minute = -1
		self.last_second = -1
		self.first_time = True

	def render_clock_face(self, dx=0, dy=0, r=0):
		"""Render the clock face with hour markers."""
		gfx = self.gfx
		hr = 1
		self.screen.circle(gfx, gfx.x0+dx, gfx.y0+dy, r, fill=gfx.bg_color)
		for posn in _compute_clock_positions(gfx.x0 + dx, gfx.y0 + dy, r - self.gfx.font_size):
			self.screen.text_box(gfx, str(hr), posn[0], posn[1], posn[0], posn[1], valign="bottom")
			hr += 1
		gfx.line_width = 3

	def render(self):
		save_color = self.gfx.color
		dirty = 0
		now = datetime.now()
		gfx = self.gfx
		dx = (gfx.x1 - gfx.x0)/2
		dy = (gfx.y1 - gfx.y0)/2
		if dx < dy: r = dx
		else: r = dy

		if self.first_time:
			self.first_time = False
			self.render_clock_face(dx, dy, r)
			dirty = 1

		if self.hour_hand and self.last_hour != now.hour:
			hr_posn = _compute_hand_posn(gfx.x0+dx, gfx.y0+dy, r*0.5, now.hour + now.minute/60 + now.second/3600, 12.0, -3.0)
			gfx.line_width = 10
			gfx.color = self.hour_hand
			self.screen.line(gfx, gfx.x0+dx, gfx.y0+dy, hr_posn[0], hr_posn[1])
			self.last_hour = now.hour
			dirty = 1

		if self.minute_hand and self.last_minute != now.minute:
			min_posn = _compute_hand_posn(gfx.x0+dx, gfx.y0+dy, r*0.66, now.minute + now.second/60, 60.0, -15.0)
			gfx.line_width = 5
			gfx.color = self.minute_hand
			self.screen.line(gfx, gfx.x0+dx, gfx.y0+dy, min_posn[0], min_posn[1])
			self.last_minute = now.minute
			dirty = 1

		if self.second_hand and self.last_second != now.second:
			sec_posn = _compute_hand_posn(gfx.x0+dx, gfx.y0+dy, r, now.second, 60.0, -15.0)
			gfx.line_width = 1
			gfx.color = self.second_hand
			self.screen.line(gfx, gfx.x0+dx, gfx.y0+dy, sec_posn[0], sec_posn[1])
			self.last_second = now.second
			dirty = 1
		self.gfx.color = save_color
		return dirty

	def exec(self):
		return self.render()

	def onEvent(self, event):
		pass

