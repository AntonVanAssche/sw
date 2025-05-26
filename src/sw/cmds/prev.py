#!/usr/bin/env python

import click

from sw.core.history import HistoryManager, HistoryReadError, HistoryWriteError
from sw.core.wallpaper import InvalidImageError, SubprocessError, WallpaperError, WallpaperManager
from sw.utils.common import err, log
from sw.utils.style import green


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
        history = hm.read()
    except HistoryReadError as e:
        err(ctx, "Failed to read wallpaper history", e)
    except Exception as e:
        err(ctx, "Unexpected error while reading wallpaper history", e)

    if len(history) < 2:
        err(ctx, "Not enough history to go back to previous wallpaper", Exception("History too short"))

    try:
        path = history[-2].path
    except Exception as e:
        err(ctx, "Failed to get previous wallpaper path", e)

    try:
        wallpaper = wm.set_wallpaper(path)
        log(f"Wallpaper set: {green(wallpaper)}", ctx)
    except (WallpaperError, InvalidImageError, SubprocessError, HistoryWriteError) as e:
        err(ctx, "Failed to set previous wallpaper", e)
    except Exception as e:
        err(ctx, "Unexpected error while setting previous wallpaper", e)
