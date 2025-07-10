#!/usr/bin/env python

from pathlib import Path

import click

from sw_cli.core.config import Config, ConfigError
from sw_cli.core.history import HistoryIndexError, HistoryManager
from sw_cli.utils.common import err, log, warn
from sw_cli.utils.style import cyan, green, red, yellow

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
            warn("Already in favorites.", ctx)
            return

        favorites.append(path)
        CONFIG.set("favorites", favorites)
        log(f"Added to {cyan('favorites')}: {green(path)}", ctx)

    except ValueError as ve:
        err(red("Invalid history index format or no current wallpaper"), ve, ctx)
    except HistoryIndexError as hie:
        err(red(f"History index out of range: {path}"), hie, ctx)
    except ConfigError as ce:
        err(red("Failed to update favorites"), ce, ctx)
    except Exception as e:
        err(red("Unexpected error while adding to favorites"), e, ctx)


@favorite_cmd.command("rm")
@click.argument("path", required=False)
@click.pass_context
def favorite_rm_cmd(ctx, path):
    """
    Remove a wallpaper from your favorites.

    You can provide the full PATH or use @N to remove by index (e.g. @2).
    If no PATH is given, it removes the current wallpaper from favorites.
    """
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
            log(f"Removed from {cyan('favorites')}: {red(removed)}", ctx)
            return

        else:
            path = str(Path(path).expanduser().resolve())

        if path not in favorites:
            log(yellow("Not in favorites."), ctx)
            return

        favorites.remove(path)
        CONFIG.set("favorites", favorites)
        log(f"Removed from {cyan('favorites')}: {red(path)}", ctx)

    except ValueError as ve:
        err(red("Invalid history index format or no current wallpaper"), ve, ctx)
    except HistoryIndexError as hie:
        err(red("No current wallpaper found"), hie, ctx)
    except IndexError as ie:
        err(red("Invalid favorite index"), ie, ctx)
    except ConfigError as ce:
        err(red("Failed to update favorites"), ce, ctx)
    except Exception as e:
        err(red("Unexpected error while removing from favorites"), e, ctx)


@favorite_cmd.command("list")
@click.pass_context
def favorite_list_cmd(ctx):
    """
    List all favorite wallpapers.
    """
    try:
        favorites = CONFIG.get("favorites", [])
    except ConfigError as ce:
        err(red("Failed to read favorites"), ce, ctx)
    except Exception as e:
        err(red("Unexpected error while listing favorites"), e, ctx)

    if favorites:
        for idx, path in enumerate(favorites, start=1):
            log(f"{yellow(str(idx))}: {green(path)}", ctx)
    else:
        warn("No favorites found.", ctx)
