#!/usr/bin/env python

import sys

import click

COLOR_MODE = "auto"


def set_color_mode(mode: str):
    # pylint: disable=global-statement
    global COLOR_MODE
    COLOR_MODE = mode.lower()


def should_color():
    if COLOR_MODE == "always":
        return True
    if COLOR_MODE == "never":
        return False
    return sys.stdout.isatty()


def style(text, **kwargs):
    return click.style(text, **kwargs) if should_color() else text


def green(text):
    return style(text, fg="green")


def yellow(text):
    return style(text, fg="yellow")


def red(text):
    return style(text, fg="red", bold=True)


def magenta(text):
    return style(text, fg="magenta")


def cyan(text):
    return style(text, fg="cyan", bold=True)


def bold(text):
    return style(text, bold=True)


def format_boolean(value: bool) -> str:
    """
    Format a boolean value as colored text.

    Args:
        value (bool): The boolean value to format.

    Returns:
        str: A colored string representation of the boolean value.
    """
    return green("True") if value else red("False")


def format_by_value(value: str, bad_values: set) -> str:
    """
    Color a string based on whether it is in the set of bad values.

    Args:
        value (str): The value to color.
        bad_values (set): A set of values considered "bad".
        ok_color (callable): A function to color "good" values.

    Returns:
        str: The colored value.
    """
    if bad_values is None:
        bad_values = set()

    return red(value) if value in bad_values else green(value)


def format_json(obj, indent=0):
    """
    Recursively format a JSON-like object with colored output.

    Args:
        obj (dict or list): The JSON-like object to format.
        indent (int): The current indentation level.

    Returns:
        str: A string representation of the object with colored keys and values.
    """
    spaces = " " * indent
    result = ""

    if isinstance(obj, dict):
        lines = []
        for i, (k, v) in enumerate(obj.items()):
            colored_key = cyan(f'"{k}"')
            colored_val = format_json(v, indent + 2)
            comma = "," if i < len(obj) - 1 else ""
            lines.append(f"{spaces}  {colored_key}: {colored_val}{comma}")
        result = "{\n" + "\n".join(lines) + f"\n{spaces}}}"

    elif isinstance(obj, list):
        lines = []
        for i, item in enumerate(obj):
            colored_item = format_json(item, indent + 2)
            comma = "," if i < len(obj) - 1 else ""
            lines.append(f"{spaces}  {colored_item}{comma}")
        result = "[\n" + "\n".join(lines) + f"\n{spaces}]"

    else:
        if isinstance(obj, str):
            result = green(f'"{obj}"')
        elif isinstance(obj, bool):
            result = yellow(str(obj).lower())
        elif obj is None:
            result = red("null")
        elif isinstance(obj, (int, float)):
            result = magenta(str(obj))
        else:
            result = green(str(obj))

    return result
