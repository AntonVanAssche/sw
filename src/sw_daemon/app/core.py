#!/usr/bin/env python

import logging

from wayland.client.memory_pool import SharedMemoryPool

from sw_daemon.compositor import Display, OutputHandler
from sw_daemon.render import ImageRenderer


# pylint: disable=too-many-instance-attributes
class SWDaemon:
    def __init__(self, image_path=None):
        self.running = True
        self.image = ImageRenderer()

        if image_path:
            self.image.load_image(image_path)
            self.width, self.height = self.image.current_width, self.image.current_height
        else:
            self.width, self.height = None, None

        self.display = Display(app=self)
        self.registry = self.display.get_registry()

        self.outputs = []
        self.pool = None

        self.logger = logging.getLogger("sw-daemon.SW")

    def on_global(self, name, interface, version):
        if interface == "wl_output":
            self.logger.info("New output detected: %s", name)
            self.registry.bind_output(name, version)

    def on_global_remove(self, name):
        self.logger.info("Output removed: %s", name)
        self.remove_output_by_name(name)

    def remove_output_by_name(self, name):
        remaining = []
        for handler in self.outputs:
            if str(handler.output) == str(name):
                self.logger.info("Cleaning up output handler for removed output: %s", name)
                handler.destroy()
            else:
                remaining.append(handler)
        self.outputs = remaining

    def assert_initialised(self):
        if not all([self.registry.wl_compositor, self.registry.wl_shm, self.registry.layer_shell]):
            return False

        existing_outputs = {handler.output for handler in self.outputs}

        for output in self.registry.outputs:
            if output in existing_outputs:
                continue

            self.logger.info("Creating handler for new output: %s", output)
            handler = OutputHandler(
                app=self,
                output=output,
                compositor=self.registry.wl_compositor,
                layer_shell=self.registry.layer_shell,
            )
            self.outputs.append(handler)

        return False

    def create_shm_buffer(self, width, height):
        if not self.pool:
            self.pool = SharedMemoryPool(self.registry.wl_shm)
        return self.pool.create_buffer(width, height)

    def draw_wallpaper(self, buffer_ptr, width, height):
        if self.image.src_image is None:
            self.logger.warning("No image loaded yet!")
            return
        self.image.copy_to_buffer(buffer_ptr, width, height)

    def redraw_surface(self, surface, width, height):
        if width == 0 or height == 0:
            return

        if not hasattr(surface, "buffer_size") or surface.buffer_size != (width, height):
            surface.buffer, surface.buffer_ptr = self.create_shm_buffer(width, height)
            surface.buffer_size = (width, height)

        self.draw_wallpaper(surface.buffer_ptr, width, height)

        surface.attach(surface.buffer, 0, 0)
        surface.damage(0, 0, width, height)
        surface.commit()

    def run(self):
        self.logger.info("Starting Wayland event loop...")
        while self.running:
            self.assert_initialised()
            self.display.dispatch()

    def set_image(self, image_path):
        self.image.load_image(image_path)
        self.width, self.height = self.image.current_width, self.image.current_height
        self.logger.info("New image loaded: %s", image_path)

        # Force all outputs to drop old buffer
        for output in self.outputs:
            if hasattr(output.surface, "buffer"):
                del output.surface.buffer
                del output.surface.buffer_ptr
                del output.surface.buffer_size

        for output in self.outputs:
            output.redraw()
