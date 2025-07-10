#!/usr/bin/env python

import click

from sw_cli.core.history import HistoryWriteError
from sw_cli.core.wallpaper import InvalidImageError, SubprocessError, WallpaperError, WallpaperManager
from sw_cli.utils.common import err, log
from sw_cli.utils.style import green


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
        log(f"Wallpaper set: {green(wallpaper)}", ctx)
    except (WallpaperError, InvalidImageError, SubprocessError, HistoryWriteError) as e:
        err("Failed to set next wallpaper", e, ctx)
    except Exception as e:
        err("Unexpected error while setting next wallpaper", e, ctx)
