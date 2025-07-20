# weather.py
# https://openweathermap.org/api/one-call-3#current

import requests
import json
from datetime import datetime
from dataclasses import dataclass
from pymirror.pmbitmap import PMBitmap
from pymirror.pmcard import PMCard
from pymirror.pmimage import PMImage

@dataclass
class ForecastConfig:
    days: int = 3  # Number of days to forecast
    days_offset: int = 0  # Offset for the forecast days
    icon_size: str = "small"  # Size of the forecast icons (None, small, medium, large)

class Forecast(PMCard):
    def __init__(self, pm, config):
        super().__init__(pm, config)
        self._forecast = ForecastConfig(**config.forecast.__dict__)
        self.subscribe("WeatherForecastEvent")
        self.dirty = False

    def _load_icon(self, icon_code: str, size: str) -> PMBitmap:
        # Load the weather icon bitmap based on the icon code and size
        scale = {"small": "", "medium": "@2x", "large": "@4x"}.get(size, "")
        icon_path = f"./weather_icons/{icon_code}{scale}.png"
        print(f"Loading weather icon from {icon_path}")
        return PMImage().load(icon_path)

    def _render(self, rect: tuple = None) -> tuple:
        ## if rect is None, don't render anything
        ## just try to render and return the bounding box
        if rect:
            dx, dy = rect
        else:
            dx, dy = 0, 0
        x0, y0, x1, y1 = 0, 0, 0, 0
        lines = 3
        cfg = self._forecast
        for i in range(cfg.days_offset, cfg.days_offset + cfg.days):
            if i >= len(self.weather_response.daily):
                print(f"Skipping day {i} as it exceeds available data")
                continue
            icon_code = self.weather_response.daily[i].weather[0].icon
            icon = self._load_icon(icon_code, cfg.icon_size)
            date = datetime.fromtimestamp(self.weather_response.daily[i].dt)
            if rect: self.bitmap.img.paste(icon, (x0 + dx, y0 + dy))
            self.gfx.color = "#fff"
            if rect: self.bitmap.rect(self.gfx, (x0 + dx, y0 + dy, x0 + icon.width + dx, y0 + icon.height + dy), fill=None)
            day = date.strftime("%a")
            desc =  self.weather_response.daily[i].weather[0].description
            temp = self.weather_response.daily[i].temp.day
            msg = f"{day}\n{desc}\n{temp}°F"
            if rect: self.bitmap.text_box(
                self.gfx,
                msg,
                (x0 + dx, y0 + icon.height + dy, x0 + icon.width + dx, y0 + icon.height + self.gfx.font_height * lines + dy),
                valign="center",
                halign="center",
                wrap="words",
            )
            x0 += icon.width
            x1 = max(x1, x0)
            y1 = max(y1, y0 + icon.height + self.gfx.font_height * lines)
            if x0 + icon.width >= self.gfx.width:
                x0 = 0
                y0 += icon.height + self.gfx.font_height * lines
        return (0, 0, x1, y1)

    def render(self, force: bool = False) -> bool:
        if not (self.dirty or force):
            return False
        self.bitmap.clear()
        bbox = self._render(None) ## render and return the bounding box
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        dx = (self.gfx.width - w) // 2
        dy = (self.gfx.height - h) // 2
        print(f"Forecast bounding box: {bbox}, x0,y0={dx},{dy}, size: {w}x{h}")
        self._render((dx, dy))
        self.dirty = False
        return True

    def onWeatherForecastEvent(self, event):
        self.dirty = True
        self.weather_response = event.data

    def exec(self) -> bool:
        return self.dirty # state changed
