##
## test out different gfx modes - esp RGB16
#
from PIL import Image, ImageDraw

class PMBitmap:
    def __init__(self, width=None, height=None, bg_color=0):
        if width is None or height is None:
            return
        # Use standard RGB mode for creation and drawing
        self.img = Image.new("RGB", (width, height), bg_color)
        self.draw = ImageDraw.Draw(self.img)
        self._bg_color = bg_color
    
    def save_16bit(self, filename):
        """Save as 16-bit RGB for frame buffer compatibility"""
        # Convert to RGB;16 only when saving
        try:
            rgb16_img = self.img.convert("RGB;16")
            rgb16_img.save(filename)
        except:
            # Fallback to regular RGB if RGB;16 conversion fails
            self.img.save(filename)

def main():
    # Create a bitmap with specific dimensions and background color
    bitmap = PMBitmap(100, 100, bg_color=(255, 255, 255))  # White background
    
    # Clear the bitmap
    bitmap.draw.rectangle((0, 0, bitmap.img.width, bitmap.img.height), fill=bitmap._bg_color)

    # Draw an ellipse with proper RGB colors
    bitmap.draw.ellipse((10, 10, 90, 90), outline=(255, 0, 0), width=2)  # Red outline
    
    # Draw a circle
    bitmap.draw.ellipse((50-30, 50-30, 50+30, 50+30), outline=(0, 0, 255), width=2)  # Blue outline

    # Draw a rectangle
    bitmap.draw.rectangle((30, 30, 70, 70), outline=(0, 255, 0), width=2)  # Green outline

    # Save as regular RGB
    bitmap.img.save("test_bitmap.png")
    
    # Save as 16-bit if needed for frame buffer
    bitmap.save_16bit("test_bitmap_16bit.png")

if __name__ == "__main__":
    main()