#!/usr/bin/env python

from pathlib import Path

import click

from sw.core.history import HistoryManager
from sw.core.wallpaper import WallpaperManager
from sw.utils.common import log


@click.command("set", short_help="Set a wallpaper from file or dir")
@click.help_option("--help", "-h")
@click.argument("path", required=False)
@click.option("--use-dir", "-d", is_flag=True, help="Use the directory of the current wallpaper.")
@click.pass_context
def set_cmd(ctx, path, use_dir):
    """
    Set the current wallpaper from a file, directory, or history index.

    PATH can be:
      @N — set wallpaper from history index N (1-based);
      a file path — use it directly;
      a directory — pick a random valid image from it.

    If PATH is not provided, the next queued wallpaper is used; if none, a random image from the default directory.
    """
    wm = WallpaperManager()

    try:
        if path and path.startswith("@"):
            index = int(path[1:]) - 1
            wallpaper = wm.set_by_history_index(index)

        elif not path and use_dir:
            hm = HistoryManager()
            current_path = hm.get_by_index(-1)
            if not current_path:
                raise ValueError("Current wallpaper is unknown.")

            directory = Path(current_path).parent
            wallpaper = wm.set_wallpaper(str(directory))

        else:
            wallpaper = wm.set_wallpaper(path)

        if not ctx.obj.get("silent"):
            log(f"Wallpaper set: {wallpaper or 'from default dir'}", silent=ctx.obj["silent"])

    except ValueError as ve:
        log(f"Invalid input: {ve}", silent=False)
    except Exception as e:
        log(f"Error setting wallpaper: {e}", silent=False)
