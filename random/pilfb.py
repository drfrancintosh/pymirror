import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time

# === CONFIGURATION ===
WIDTH = 1920
HEIGHT = 1080
FBDEV = "/dev/fb0"

def rgb888_to_rgb565(r, g, b):
    """Convert 8-bit RGB to 16-bit RGB565 (matches framebuffer format)"""
    # Red: 5 bits, Green: 6 bits, Blue: 5 bits
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)

def image_to_rgb565(img):
    """Convert a Pillow RGB image to raw RGB565 bytes using numpy"""
    # Convert image to RGB (ensure no alpha channel) and then to numpy array
    img = img.convert("RGB")  # Make sure the image is in RGB mode
    img_array = np.array(img, dtype=np.uint16)  # Convert to uint16 for correct shifting

    # Perform the conversion to RGB565 for all pixels at once
    rgb565_array = ((img_array[..., 0] >> 3) << 11) | \
                   ((img_array[..., 1] >> 2) << 5) | \
                   (img_array[..., 2] >> 3)

    # Convert the numpy array to bytes (little-endian)
    raw = rgb565_array.astype(np.uint16).tobytes()
    return raw

def main():
    # Create Pillow image
    img = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(img)

    # Draw a red rectangle and some text
    draw.rectangle((100, 100, 300, 200), fill="red")
    draw.rectangle((150, 150, 350, 250), fill="green")
    draw.rectangle((200, 200, 400, 300), fill="blue")
    draw.rectangle((250, 250, 450, 350), fill="white")
    font = ImageFont.load_default()
    draw.text((120, 130), "Hello, framebuffer!", font=font, fill="white")

    # Convert to RGB565
    raw = image_to_rgb565(img)

    # Write to framebuffer
    with open(FBDEV, "wb") as f:
        f.write(raw)

if __name__ == "__main__":
    main()
