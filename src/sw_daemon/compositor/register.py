#!/usr/bin/python

import wayland
from wayland.client import wayland_class


# pylint: disable=no-member
@wayland_class("wl_registry")
class Registry(wayland.wl_registry):
    def __init__(self, app=None):
        super().__init__(app=app)
        self.wl_compositor = None
        self.wl_shm = None
        self.layer_shell = None
        self.outputs = []

    def on_global(self, name, interface, version):
        if interface == "wl_compositor":
            self.wl_compositor = self.bind(name, interface, version)
        elif interface == "wl_shm":
            self.wl_shm = self.bind(name, interface, version)
        elif interface == "zwlr_layer_shell_v1":
            self.layer_shell = self.bind(name, interface, version)
        elif interface == "wl_output":
            self.outputs.append(self.bind(name, interface, version))
