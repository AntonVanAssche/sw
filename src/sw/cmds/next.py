#!/usr/bin/env python

import click

from sw.core.wallpaper import WallpaperManager
from sw.utils.common import log


@click.command("next", short_help="Set the next wallpaper")
@click.help_option("--help", "-h")
@click.pass_context
def next_cmd(ctx):
    """
    Set the next wallpaper from the queue.

    If the queue is empty, a random image from the default wallpaper directory is used instead.

    This is equivalent to running: sw set
    """
    wm = WallpaperManager()

    try:
        wallpaper = wm.set_wallpaper()
        if not ctx.obj.get("silent"):
            log(f"Wallpaper set: {wallpaper or 'from default dir'}", silent=ctx.obj["silent"])
    except Exception as e:
        raise Exception(f"Error setting wallpaper: {e}") from e
