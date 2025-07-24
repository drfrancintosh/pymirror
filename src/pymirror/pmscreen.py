import os
from dataclasses import dataclass
from PIL import Image
from pymirror.pmgfx import PMGfx
from pymirror.pmbitmap import PMBitmap
import numpy as np

@dataclass
class PMScreenConfig:
        width: int = 1920
        height: int = 1080
        rotate: int = 0  # Rotation angle in degrees
        color: str = "#fff"  # default color
        bg_color: str = "#000"  # default background color
        text_color: str = color
        text_bg_color: str = None
        line_width: int = 1
        font_name: str = "Roboto-Regular"
        font_size: int = 64
        output_file: str = None
        frame_buffer: str = "/dev/fb"  # Path to framebuffer device

class PMScreen:
    def __init__(self, _config):
        self._config = _config
        ## by convention the config for an object is _classname
        self._screen = _screen = PMScreenConfig(**_config.screen.__dict__) if _config.screen else PMScreenConfig()
        self.bitmap = PMBitmap(_screen.width, _screen.height, _screen.bg_color)
        self.gfx = gfx = PMGfx()
        gfx.rect = (0, 0, _screen.width-1, _screen.height-1)
        gfx.color = _screen.color or gfx.color
        gfx.bg_color = _screen.bg_color or gfx.bg_color
        gfx.text_color = _screen.text_color or gfx.text_color
        gfx.text_bg_color = _screen.text_bg_color or gfx.text_bg_color
        gfx.line_width = _screen.line_width or gfx.line_width
        gfx.set_font(gfx.font_name, gfx.font_size)

        self._hard_clear()

    def _hard_clear(self):
        """Clear the framebuffer by writing zeros to it."""
        if self._screen.frame_buffer:
            # Open the framebuffer device and write zeros to it
            with open(self._screen.frame_buffer, "wb") as f:
                f.write(b'\x00' * (1920 * 1080 * 2))  # Assuming RGB565 format, 2 bytes per pixel

    def _write_framebuffer(self, img: Image.Image) -> None:
        """Write the image to the framebuffer."""
        # self._screen.frame_buffer = "./fb0.jpg"
        if self._screen.frame_buffer:
            # print(f"Writing to framebuffer: {self._screen.frame_buffer}")
            from clib import rgba_to_rgb16, free_rgb16
            # print(f"Image size: {img.size}, mode: {img.mode}")
            raw = img.tobytes("raw")
            # print(f"Raw image size: {len(raw)} bytes")
            rgb565 = rgba_to_rgb16(raw, img.width, img.height)
            # print(f"Converted to RGB565 size: {len(rgb565)} bytes")
            with open(self._screen.frame_buffer, "wb") as f:
                # print(f"Saving RGB565 image to {self._screen.frame_buffer}")
                f.write(rgb565)
            # print("Freeing RGB565 memory")
            # free_rgb16(rgb565)
            # print("Framebuffer write complete")

    def _atomic_write(self, img: Image.Image) -> None:
        if self._screen.output_file:
            self.bitmap.img.convert("RGB").save(self._screen.output_file+".tmp", "JPEG")
            os.rename(self._screen.output_file+".tmp", self._screen.output_file)

    def flush(self) -> None:
        img = self.bitmap.img
        if self._screen.rotate:
            img = img.rotate(self._screen.rotate, expand=True) 
        self._write_framebuffer(img)
        self._atomic_write(img)
