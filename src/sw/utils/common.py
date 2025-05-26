#!/usr/bin/env python

import re
import sys

import notify2
from PIL import Image

from sw.utils.style import bold, red, yellow

Image.MAX_IMAGE_PIXELS = None
ANSI_ESCAPE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)


def notify(title: str, message: str):
    try:
        notify2.init("Switch Wallpaper")
        n = notify2.Notification(title, message)
        n.set_timeout(3000)
        n.show()
    except Exception:
        pass


def log(message: str, ctx: dict = None):
    ctx = ctx or {}
    silent = ctx.obj.get("silent", False)
    notify_enabled = ctx.obj.get("notify", True)

    if silent:
        return

    if notify_enabled:
        clean_message = strip_ansi(message)
        notify("Switch Wallpaper (script)", clean_message)

    print(message)


def warn(message: str, ctx: dict = None):
    ctx = ctx or {}
    silent = ctx.obj.get("silent", False)
    notify_enabled = ctx.obj.get("notify", True)

    if silent:
        return

    if sys.stderr.isatty():
        print(bold(yellow(message)), file=sys.stderr)
    elif notify_enabled:
        notify("Switch Wallpaper (script)", f"Warning: {message}")
    else:
        print(f"Warning: {message}", file=sys.stderr)


def err(message: str, exc: Exception, ctx: dict = None):
    ctx = ctx or {}
    silent = ctx.obj.get("silent", False)
    notify_enabled = ctx.obj.get("notify", True)

    if silent:
        ctx.exit(1)

    error_msg = f"{message}: {exc}"
    if sys.stderr.isatty():
        print(f"{bold(red('Error:'))} {error_msg}", file=sys.stderr)
    elif notify_enabled:
        notify("Switch Wallpaper (script)", f"Error: {error_msg}")
    else:
        print(f"Error: {error_msg}", file=sys.stderr)

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
