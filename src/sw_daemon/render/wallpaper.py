#!/usr/bin/python

import ctypes
import logging

from PIL import Image


class ImageRenderer:
    def __init__(self):
        self.src_image = None
        self.current_width = 0
        self.current_height = 0

        self.logger = logging.getLogger("sw-daemon.ImageRenderer")

    def load_image(self, path):
        self.logger.info("Loading image from: %s", path)

        try:
            img = Image.open(path).convert("RGBA")
        except Exception as e:
            self.logger.error("Failed to load image '%s': %s", path, e)
            raise

        self.src_image = img
        self.current_width, self.current_height = img.size

        self.logger.debug("Loaded image size: %sx%s", self.current_width, self.current_height)
        return True

    def _resize_and_crop(self, target_width, target_height):
        """Resize the image to cover and crop to the target dimensions."""
        src_w, src_h = self.src_image.size

        scale = max(target_width / src_w, target_height / src_h)
        new_w = int(src_w * scale)
        new_h = int(src_h * scale)

        self.logger.debug("Resized image dimensions: %sx%s", new_w, new_h)

        # pylint: disable=no-member
        resized = self.src_image.resize((new_w, new_h), Image.LANCZOS)

        left = (new_w - target_width) // 2
        top = (new_h - target_height) // 2

        cropped = resized.crop((left, top, left + target_width, top + target_height))
        return cropped

    def _convert_to_bgra_bytes(self, pil_image):
        """Convert RGBA PIL image to BGRA bytes."""
        r, g, b, a = pil_image.split()
        bgra_image = Image.merge("RGBA", (b, g, r, a))
        return bgra_image.tobytes()

    def copy_to_buffer(self, buffer, width, height):
        if self.src_image is None:
            self.logger.error("No image loaded! Cannot copy to buffer.")
            return False

        self.logger.debug("Source image size: %sx%s", *self.src_image.size)
        self.logger.debug("Target buffer size: %sx%s", width, height)

        cropped = self._resize_and_crop(width, height)
        data = self._convert_to_bgra_bytes(cropped)

        ctypes.memmove(buffer, data, len(data))

        self.logger.debug("Image successfully copied to buffer.")
        return True
