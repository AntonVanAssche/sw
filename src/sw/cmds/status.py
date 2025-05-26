#!/usr/bin/env python

import re
from pathlib import Path

import click

from sw.core.history import HistoryManager, HistoryReadError
from sw.core.timer import TimerError, TimerManager
from sw.utils.common import err, log
from sw.utils.style import format_by_value, green


@click.command("status", short_help="Show current wallpaper status")
@click.help_option("--help", "-h")
@click.option("-n", "--name", is_flag=True, help="Show the pretty name of the current wallpaper")
@click.option("-d", "--directory", is_flag=True, help="Show the directory of the current wallpaper")
@click.option("-P", "--hide-path", is_flag=True, help="Hide the path of the current wallpaper")
@click.option("-T", "--hide-timer", is_flag=True, help="Hide the timer information")
@click.pass_context
def status_cmd(ctx, name, directory, hide_path, hide_timer):
    """
    Show information about the current wallpaper.

    Displays details about the wallpaper currently in use,
    including its file path, name, directory, and time left
    until the next wallpaper change (if a timer is active).
    """
    hm = HistoryManager()
    tm = TimerManager()

    try:
        wallpaper_info = hm.get_by_index(-1)
    except HistoryReadError as e:
        err("Failed to read current wallpaper from history", e, ctx)
    except Exception as e:
        err("Unexpected error while getting current wallpaper", e, ctx)

    try:
        timer_info = tm.time_left() if not hide_timer else None
    except TimerError as e:
        err("Failed to get timer info", e, ctx)
    except Exception as e:
        err("Unexpected error while getting timer info", e, ctx)

    def prettify(path: str) -> str:
        name = re.sub(r"^.*[\\/]", "", path)
        name = re.sub(r"[-_]", " ", name)
        name = re.sub(r"\.[^.]+$", "", name)
        name = re.sub(r"\b0*(\d+)\b", r"(\1)", name)
        return name

    parts = []

    if name:
        parts.append(f"Name: {green(prettify(wallpaper_info))}")

    if not hide_path:
        parts.append(f"Path: {green(wallpaper_info)}")

    if directory:
        parts.append(f"Directory: {green(str(Path(wallpaper_info).parent))}")

    if not hide_timer and timer_info:
        parts.append(f"Timer: {format_by_value(tm.time_left(), ("Timer is not active", "Timer expired recently"))}")

    log("\n".join(parts), ctx=ctx)
