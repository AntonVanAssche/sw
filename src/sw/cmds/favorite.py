#!/usr/bin/env python

from pathlib import Path

import click

from sw.core.config import Config, ConfigError
from sw.core.history import HistoryIndexError, HistoryManager
from sw.utils.common import err, log, warn
from sw.utils.style import cyan, green, red, yellow

CONFIG = Config()


def get_current_wallpaper() -> str:
    """Get the current wallpaper path."""
    hm = HistoryManager()

    try:
        return hm.get_by_index(-1)
    except HistoryIndexError as e:
        raise ValueError("No current wallpaper found.") from e


# pylint: disable=unused-argument
@click.group("favorite", short_help="Manage favorite wallpapers")
@click.help_option("--help", "-h")
@click.pass_context
def favorite_cmd(ctx):
    """
    Manage your favorite wallpapers.

    This command allows you to add, remove, and list wallpapers in your
    favorites.
    """


@favorite_cmd.command("add")
@click.argument("path", required=False)
@click.pass_context
def favorite_add_cmd(ctx, path):
    """
    Add a wallpaper to your favorites.
    If PATH is not provided, the current wallpaper is used.
    """
    silent = ctx.obj.get("silent", False)

    try:
        if not path:
            path = get_current_wallpaper()

        if path.startswith("@"):
            index = int(path[1:]) - 1
            hm = HistoryManager()
            path = hm.get_by_index(index)

        path = str(Path(path).expanduser().resolve())
        favorites = CONFIG.get("favorites", [])

        if path in favorites:
            warn("Already in favorites.", silent=silent)
            return

        favorites.append(path)
        CONFIG.set("favorites", favorites)
        log(f"Added to {cyan('favorites')}: {green(path)}", silent=silent)

    except ValueError as ve:
        err(ctx, red("Invalid history index format or no current wallpaper"), ve)
    except HistoryIndexError as hie:
        err(ctx, red(f"History index out of range: {path}"), hie)
    except ConfigError as ce:
        err(ctx, red("Failed to update favorites"), ce)
    except Exception as e:
        err(ctx, red("Unexpected error while adding to favorites"), e)


@favorite_cmd.command("rm")
@click.argument("path", required=False)
@click.pass_context
def favorite_rm_cmd(ctx, path):
    """
    Remove a wallpaper from your favorites.

    You can provide the full PATH or use @N to remove by index (e.g. @2).
    If no PATH is given, it removes the current wallpaper from favorites.
    """
    silent = ctx.obj.get("silent", False)

    try:
        favorites = CONFIG.get("favorites", [])

        if not path:
            path = str(Path(get_current_wallpaper()).expanduser().resolve())

        elif path.startswith("@"):
            index = int(path[1:]) - 1
            if index < 0 or index >= len(favorites):
                raise IndexError(f"Invalid index: {index + 1}")

            removed = favorites.pop(index)
            CONFIG.set("favorites", favorites)
            log(f"Removed from {cyan('favorites')}: {red(removed)}", silent=silent)
            return

        else:
            path = str(Path(path).expanduser().resolve())

        if path not in favorites:
            log(yellow("Not in favorites."), silent=silent)
            return

        favorites.remove(path)
        CONFIG.set("favorites", favorites)
        log(f"Removed from {cyan('favorites')}: {red(path)}", silent=silent)

    except ValueError as ve:
        err(ctx, red("Invalid history index format or no current wallpaper"), ve)
    except HistoryIndexError as hie:
        err(ctx, red("No current wallpaper found"), hie)
    except IndexError as ie:
        err(ctx, red("Invalid favorite index"), ie)
    except ConfigError as ce:
        err(ctx, red("Failed to update favorites"), ce)
    except Exception as e:
        err(ctx, red("Unexpected error while removing from favorites"), e)


@favorite_cmd.command("list")
@click.pass_context
def favorite_list_cmd(ctx):
    """
    List all favorite wallpapers.
    """
    silent = ctx.obj.get("silent", False)

    try:
        favorites = CONFIG.get("favorites", [])
    except ConfigError as ce:
        err(ctx, red("Failed to read favorites"), ce)
    except Exception as e:
        err(ctx, red("Unexpected error while listing favorites"), e)

    if favorites:
        for idx, path in enumerate(favorites, start=1):
            log(f"{yellow(str(idx))}: {green(path)}", silent=silent)
    else:
        warn("No favorites found.", silent=silent)
