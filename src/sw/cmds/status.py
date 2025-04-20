#!/usr/bin/env python

import re
from pathlib import Path

import click

from sw.core.history import HistoryManager
from sw.core.timer import TimerManager
from sw.utils.common import log


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

    wallpaper_info = hm.get_by_index(-1)
    timer_info = tm.time_left() if not hide_timer else None

    def prettify(path: str) -> str:
        name = re.sub(r"^.*[\\/]", "", path)
        name = re.sub(r"[-_]", " ", name)
        name = re.sub(r"\.[^.]+$", "", name)
        name = re.sub(r"\b0*(\d+)\b", r"(\1)", name)
        return name

    parts = []

    if name:
        parts.append(f"Name: {prettify(wallpaper_info)}")

    if not hide_path:
        parts.append(f"Path: {wallpaper_info}")

    if directory:
        parts.append(f"Directory: {Path(wallpaper_info).parent}")

    if not hide_timer and timer_info:
        parts.append(f"Timer: {timer_info}")

    log("\n".join(parts), silent=ctx.obj.get("silent"))
