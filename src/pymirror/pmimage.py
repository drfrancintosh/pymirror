from PIL import Image
from pymirror.pmbitmap import PMBitmap

class PMImage(PMBitmap):
    def __init__(self, path: str = None, width: int = None, height: int = None, scale: str = None):
        super().__init__()
        if path is not None:
            self.load(path, width, height, scale)

    def scale_to_fit(self, image, target_width, target_height):
        """Scale image to fit within bounds, maintaining aspect ratio"""
        original_width, original_height = image.size
        
        # Calculate scale factor (use the smaller ratio)
        scale_x = target_width / original_width
        scale_y = target_height / original_height
        scale = min(scale_x, scale_y)  # Smaller ratio ensures it fits
        
        # Calculate new dimensions
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        return image.resize((new_width, new_height), Image.LANCZOS)

    def scale_to_fill(self, image, target_width, target_height):
        """Scale image to fill entire area, cropping excess"""
        original_width, original_height = image.size
        
        # Calculate scale factor (use the larger ratio)
        scale_x = target_width / original_width
        scale_y = target_height / original_height
        scale = max(scale_x, scale_y)  # Larger ratio ensures it fills
        
        # Scale the image
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        scaled_image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Center crop to target size
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        return scaled_image.crop((left, top, right, bottom))

    def load(self, image_path, width=None, height=None, scale=None):
        image = Image.open(image_path)
        image = image.convert("RGBA")  # Ensure the image is in RGB format
        if width is not None and height is not None:
            if scale == "fit":
                # print(f"Scaling image to fit within {width}x{height}")
                image = self.scale_to_fit(image, width, height)
            elif scale == "fill":
                # print(f"Scaling image to fill {width}x{height}")
                image = self.scale_to_fill(image, width, height)
            elif scale == "stretch":
                # Default to resizing without aspect ratio preservation
                # print(f"Stretching image to {width}x{height}")
                image = image.resize((width, height), Image.LANCZOS)
        raw_bytes = image.tobytes("raw")
        ### Convert raw bytes to RGB565 format
        arr = bytearray(raw_bytes)
        # print(f"Image bytes length: {len(arr)}")
        for i in range(0, len(arr), 4):
            r = (arr[i] >> 3) & 0x1F
            g = (arr[i+1] >> 2) & 0x3F
            b = (arr[i+2] >> 3) & 0x1F
            arr[i + 2] = (r << 3) | (g >> 3)
            arr[i + 1] = 0
            arr[i + 0] = ((g & 0x07) << 5) | b
            arr[i + 3] = 0
        bytes_data = bytes(arr)  # make it immutable
        image = Image.frombytes("I", (image.width, image.height), bytes_data)
        self.set_image(image)
        return image