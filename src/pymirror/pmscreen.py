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
        if self._screen.frame_buffer:
            raw = img.tobytes("raw")
            with open(self._screen.frame_buffer, "wb") as f:
                f.write(raw[0::2])  # Write every second byte for RGB565 format

    def _atomic_write(self, img: Image.Image) -> None:
        if self._screen.output_file:
            raw = img.tobytes("raw")[0::2]
            arr = np.frombuffer(raw, dtype=np.uint16).reshape((self.gfx.height, self.gfx.width))

            # Unpack RGB565 to 8-bit RGB
            r = ((arr >> 11) & 0x1F) << 3
            g = ((arr >> 5) & 0x3F) << 2
            b = (arr & 0x1F) << 3

            rgb = np.dstack((r, g, b)).astype(np.uint8)

            # Create a PIL Image
            img = Image.fromarray(rgb, "RGB")
            img.save(self._screen.output_file+".tmp", "JPEG")
            os.rename(self._screen.output_file+".tmp", self._screen.output_file)


    def flush(self) -> None:
        img = self.bitmap.img
        if self._screen.rotate:
            img = img.rotate(self._screen.rotate, expand=True) 
        self._write_framebuffer(img)
        self._atomic_write(img)
