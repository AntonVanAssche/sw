#!/usr/bin/env python

import re
import sys

import notify2
from PIL import Image

from sw_cli.utils.style import bold, red, yellow

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


def resolve_indexed_path(index, entries):
    """
    Resolve an indexed path from favorites or history.
    Index is 1-based, e.g. @1 means entries[0].
    Can be negative for reverse indexing (e.g. @-1 is entries[-1]).
    """
    try:
        idx = int(index[1:])
        if idx == 0:
            raise ValueError("Index must not be 0 (1-based indexing)")
        if idx > 0:
            return entries[idx - 1]

        return entries[idx]
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid index '{index}' for entries: {entries}") from e


def is_valid_image(path: str) -> bool:
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except (IOError, SyntaxError):
        return False


def prettify_time(seconds: float) -> str:
    """Convert seconds to a human-readable time string."""
    if seconds < 0:
        return "Invalid time"

    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    parts = []
    if hours:
        parts.append(f"{int(hours)} hours")
    if minutes:
        parts.append(f"{int(minutes)} minutes")
    if seconds:
        parts.append(f"{int(seconds)} seconds")

    return ", ".join(parts) if parts else "a moment"


def prettify_path(path: str) -> str:
    """Convert a file path to a more readable format."""
    name = re.sub(r"^.*[\\/]", "", path)
    name = re.sub(r"[-_]", " ", name)
    name = re.sub(r"\.[^.]+$", "", name)
    name = re.sub(r"\b0*(\d+)\b", r"(\1)", name)
    return name.strip()
