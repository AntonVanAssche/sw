#!/usr/bin/env python

import logging

from protocols.wlr_layer_shell_unstable_v1 import ZwlrLayerShellV1, ZwlrLayerSurfaceV1


class OutputHandler:
    def __init__(self, app, output, compositor, layer_shell):
        self.app = app
        self.output = output
        self.surface = compositor.create_surface()

        self.logger = logging.getLogger("sw-daemon.OutputHandler")
        self.logger.info("Creating layer surface for output: %s", self.output)

        self.layer_surface = layer_shell.get_layer_surface(
            self.surface, output, ZwlrLayerShellV1.layer.background, "sw"
        )
        self.layer_surface.events.configure += self.on_configure

        self.layer_surface.set_anchor(
            ZwlrLayerSurfaceV1.anchor.top
            | ZwlrLayerSurfaceV1.anchor.bottom
            | ZwlrLayerSurfaceV1.anchor.left
            | ZwlrLayerSurfaceV1.anchor.right
        )
        self.layer_surface.set_exclusive_zone(-1)
        self.surface.commit()

        self.width = 0
        self.height = 0

    def on_configure(self, serial, width, height):
        self.logger.info("Configure event for %s: %sx%s", self.output, width, height)
        self.layer_surface.ack_configure(serial)
        self.app.redraw_surface(self.surface, width, height)
        self.width = width
        self.height = height

    def redraw(self):
        if self.width > 0 and self.height > 0:
            self.logger.debug("Redrawing output %s at %sx%s", self.output, self.width, self.height)
            self.app.redraw_surface(self.surface, self.width, self.height)

    def destroy(self):
        self.logger.info("Destroying surfaces for output: %s", self.output)
        self.layer_surface.destroy()
        self.surface.destroy()
