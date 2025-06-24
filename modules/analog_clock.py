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
		self.gfx.bg_color = None # clear background
		self.render_clock_face()
		self.hour = 0
		self.minute = 0
		self.second = 0
		self.last_hour = -1
		self.last_minute = -1
		self.last_second = -1
		self.first_time = True

	def render_clock_face(self):
		"""Render the clock face with hour markers."""
		gfx = self.gfx
		dx = (gfx.x1 - gfx.x0) / 2
		dy = (gfx.y1 - gfx.y0) / 2
		if dx < dy:
			r = dx
		else:
			r = dy
		gfx.text_color = (192, 192, 192)
		hr = 1
		for posn in _compute_clock_positions(gfx.x0 + dx, gfx.y0 + dy, r - self.gfx.font_size):
			self.screen.text_box(gfx, str(hr), posn[0], posn[1], posn[0], posn[1], valign="bottom")
			hr += 1
		gfx.color = (192, 192, 192)
		gfx.line_width = 3
		self.screen.circle(gfx, gfx.x0+dx, gfx.y0+dy, r )

	def render(self):
		if self.first_time:
			self.render_clock_face()
			self.first_time = False
		# now = datetime.now()
		# gfx = self.gfx
		# dx = (gfx.x1 - gfx.x0)/2
		# dy = (gfx.y1 - gfx.y0)/2
		# if dx < dy:
		# 	r = dx
		# else:
		# 	r = dy
		# hr = 1
		# gfx.text_color = (192, 192, 192)
		# for posn in _compute_clock_positions(gfx.x0+dx, gfx.y0+dy, r-self.gfx.font_size):
		# 	self.screen.text_box(gfx, str(hr), posn[0], posn[1], posn[0], posn[1], valign="bottom")
		# 	hr += 1
		# gfx.color = (192, 192, 192)
		# gfx.line_width = 3
		# self.screen.circle(gfx, gfx.x0+dx, gfx.y0+dy, r )

		# hr_posn = _compute_hand_posn(gfx.x0+dx, gfx.y0+dy, r*0.5, now.hour + now.minute/60 + now.second/3600, 12.0, -3.0)
		# gfx.line_width = 10
		# self.screen.line(gfx, gfx.x0+dx, gfx.y0+dy, hr_posn[0], hr_posn[1])

		# min_posn = _compute_hand_posn(gfx.x0+dx, gfx.y0+dy, r*0.66, now.minute + now.second/60, 60.0, -15.0)
		# gfx.line_width = 5 
		# gfx.color = (0, 64, 128)
		# self.screen.line(gfx, gfx.x0+dx, gfx.y0+dy, min_posn[0], min_posn[1])

		# sec_posn = _compute_hand_posn(gfx.x0+dx, gfx.y0+dy, r, now.second, 60.0, -15.0)
		# gfx.line_width = 1
		# gfx.color = (128, 128, 0)
		# self.screen.line(gfx, gfx.x0+dx, gfx.y0+dy, sec_posn[0], sec_posn[1])
		pass

	def exec(self):
		self.render()

	def onEvent(self, event):
		pass

