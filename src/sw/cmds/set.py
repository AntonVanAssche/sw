#!/usr/bin/env python

import random
from pathlib import Path

import click

from sw.core.config import Config
from sw.core.history import HistoryIndexError, HistoryManager, HistoryWriteError
from sw.core.wallpaper import InvalidImageError, SubprocessError, WallpaperError, WallpaperManager
from sw.utils.common import err, log, warn
from sw.utils.style import green


def _resolve_favorite_path(path, favorites):
    if not favorites:
        return None

    if path and path.startswith("@"):
        index = int(path[1:]) - 1

        if not 0 <= index < len(favorites):
            raise HistoryIndexError(f"Favorite index out of range: {index + 1}")

        return favorites[index]

    if not path:
        return random.choice(favorites)

    return path


def _set_wallpaper_by_history_index(wm, path):
    index = int(path[1:]) - 1
    wallpaper = wm.set_by_history_index(index)

    if not wallpaper:
        raise HistoryIndexError(f"History index out of range: {index + 1}")

    return wallpaper


@click.command("set", short_help="Set a wallpaper from file or dir")
@click.help_option("--help", "-h")
@click.argument("path", required=False)
@click.option("--use-dir", "-d", is_flag=True, help="Use the directory of the current wallpaper.")
@click.option("--favorite", "-f", is_flag=True, help="Select a wallpaper from favorites.")
@click.pass_context
def set_cmd(ctx, path, use_dir, favorite):
    """
    Set the current wallpaper from a file, directory, or index.

    PATH can be:
      @N — set wallpaper from history index N (or favorite index N if -f is used);
      a file path — use it directly;
      a directory — pick a random valid image from it.

    If no PATH is provided:
      - with -f — pick a random favorite;
      - with -d — pick a random image from the current wallpaper's directory;
      - otherwise — use the next queued wallpaper or a random one from the default
      directory.
    """
    wm = WallpaperManager()
    config = Config()
    wallpaper = None

    try:
        if favorite:
            favorites = config.get("favorites", [])
            resolved_path = _resolve_favorite_path(path, favorites)
            if resolved_path is None:
                warn("No favorites found. Falling back to default wallpapers.", ctx)
                path = None
            else:
                path = resolved_path

        elif path and path.startswith("@"):
            wallpaper = _set_wallpaper_by_history_index(wm, path)

        if wallpaper is None and not path and use_dir:
            current_path = HistoryManager().get_by_index(-1)
            if not current_path:
                err("Current wallpaper is unknown", ValueError("Missing history"), ctx)
            path = str(Path(current_path).parent)

        if wallpaper is None:
            wallpaper = wm.set_wallpaper(path)

        log(f"Wallpaper set: {green(wallpaper)}", ctx)

    except ValueError as ve:
        err("Invalid index format", ve, ctx)
    except HistoryIndexError as hi:
        err("Index out of range", hi, ctx)
    except (WallpaperError, InvalidImageError, SubprocessError, HistoryWriteError) as e:
        err("Failed to set wallpaper", e, ctx)
    except Exception as e:
        err("Unexpected error", e, ctx)
