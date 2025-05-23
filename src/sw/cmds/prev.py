#!/usr/bin/env python

import click

from sw.core.history import HistoryManager
from sw.core.wallpaper import WallpaperManager
from sw.utils.common import log


@click.command("prev", short_help="Set the previous wallpaper in the queue")
@click.help_option("--help", "-h")
@click.pass_context
def prev_cmd(ctx):
    """
    Set the previous wallpaper from the history.

    This command sets the wallpaper to the second-to-last entry in the history.

    If no previous entry is available, an error is raised.
    """
    wm = WallpaperManager()
    hm = HistoryManager()

    try:
        path = hm.read()[-2].path
        wallpaper = wm.set_wallpaper(path)
        if not ctx.obj.get("silent"):
            log(f"Wallpaper set: {wallpaper or 'from default dir'}", silent=ctx.obj["silent"])
    except Exception as e:
        raise Exception(f"Error setting wallpaper: {e}") from e
