#!/usr/bin/python

import ctypes
import logging
import os

from PIL import Image


class ImageRenderer:
    def __init__(self):
        self.src_image = None
        self.current_width = 0
        self.current_height = 0

        self.logger = logging.getLogger("sw-daemon.ImageRenderer")

    def load_image(self, file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, file)

        self.logger.info(f"Loading image from: {path}")

        try:
            img = Image.open(path).convert("RGBA")
        except Exception as e:
            self.logger.error(f"Failed to load image '{path}': {e}")
            raise

        self.src_image = img
        self.current_width, self.current_height = img.size

        self.logger.debug(f"Loaded image size: {self.current_width}x{self.current_height}")
        return True

    def copy_to_buffer(self, buffer, width, height):
        if self.src_image is None:
            self.logger.error("No image loaded! Cannot copy to buffer.")
            return False

        src_w, src_h = self.src_image.size
        self.logger.debug(f"Source image size: {src_w}x{src_h}")
        self.logger.debug(f"Target buffer size: {width}x{height}")

        # Scale to cover the entire output
        scale = max(width / src_w, height / src_h)
        new_w = int(src_w * scale)
        new_h = int(src_h * scale)

        self.logger.debug(f"Resized image dimensions: {new_w}x{new_h}")

        resized = self.src_image.resize((new_w, new_h), Image.LANCZOS)

        # Center crop
        left = (new_w - width) // 2
        top = (new_h - height) // 2
        cropped = resized.crop((left, top, left + width, top + height))

        # Convert RGBA -> BGRA
        r, g, b, a = cropped.split()
        bgra_image = Image.merge("RGBA", (b, g, r, a))

        data = bgra_image.tobytes()
        ctypes.memmove(buffer, data, len(data))

        self.logger.debug("Image successfully copied to buffer.")
        return True
