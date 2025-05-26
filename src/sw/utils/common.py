#!/usr/bin/env python

import re
import sys

import notify2
from PIL import Image

from sw.utils.style import bold, red

Image.MAX_IMAGE_PIXELS = None
ANSI_ESCAPE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)


def log(message: str, ctx: dict = None):
    ctx = ctx or {}
    silent = ctx.obj.get("silent", False)
    notify = ctx.obj.get("notify", True)

    if silent:
        return

    if notify:
        try:
            notify2.init("Switch Wallpaper")
            clean_message = strip_ansi(message)
            n = notify2.Notification("Switch Wallpaper (script)", clean_message)
            n.set_timeout(3000)
            n.show()
        except Exception as e:
            print(message)

        return

    print(message)


def warn(message: str, silent: bool = False):
    if sys.stderr.isatty():
        print(bold(yellow(message)), file=sys.stderr)
    else:
        notify2.init("Switch Wallpaper")
        n = notify2.Notification("Switch Wallpaper (script)", f"Error: {message}")
        n.set_timeout(3000)
        n.show()


def err(ctx: str, message: str, exc: Exception):
    if sys.stderr.isatty():
        print(f"{bold(red('Error:'))} {message}: {exc}", file=sys.stderr)
    else:
        notify2.init("Switch Wallpaper")
        n = notify2.Notification("Switch Wallpaper (script)", f"Error: {message}")
        n.set_timeout(3000)
        n.show()

    ctx.exit(1)


def replace_lines_in_file(filepath: str, patterns: dict[str, str]):
    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        for pattern, replacement in patterns.items():
            line = re.sub(pattern, replacement, line)
        new_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as file:
        file.writelines(new_lines)


def is_valid_image(path: str) -> bool:
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except (IOError, SyntaxError):
        return False
