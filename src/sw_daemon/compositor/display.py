#!/usr/bin/python

import sys

import wayland
from wayland.client import wayland_class


# pylint: disable=no-member
@wayland_class("wl_display")
class Display(wayland.wl_display):

    def __init__(self, app=None):
        super().__init__(app=app)

    def on_error(self, object_id, code, message):
        print(f"Error: {object_id} {code} {message}")
        sys.exit(1)
