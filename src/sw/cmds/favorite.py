#!/usr/bin/env python

from pathlib import Path

import click

from sw.core.config import Config
from sw.core.history import HistoryManager
from sw.utils.common import log

CONFIG = Config()


def get_current_wallpaper() -> str:
    """Get the current wallpaper path."""
    hm = HistoryManager()

    try:
        return hm.get_by_index(-1)
    except IndexError:
        raise ValueError("No current wallpaper found.")


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
    silent = ctx.obj.get("silent")

    if not path:
        path = get_current_wallpaper()

    if path.startswith("@"):
        try:
            index = int(path[1:]) - 1
            hm = HistoryManager()
            path = hm.get_by_index(index)
        except (ValueError, IndexError):
            log(f"Invalid history index: {path}", silent=silent)
            return

    path = str(Path(path).expanduser().resolve())
    favorites = CONFIG.get("favorites", [])

    if path in favorites:
        log("Already in favorites.", silent=silent)
        return

    favorites.append(path)
    CONFIG.set("favorites", favorites)
    log(f"Added to favorites: {path}", silent=silent)


@favorite_cmd.command("rm")
@click.argument("path", required=False)
@click.pass_context
def favorite_rm_cmd(ctx, path):
    """
    Remove a wallpaper from your favorites.

    You can provide the full PATH or use @N to remove by index (e.g. @2).
    If no PATH is given, it removes the current wallpaper from favorites.
    """
    silent = ctx.obj.get("silent")
    favorites = CONFIG.get("favorites", [])

    if not path:
        path = str(Path(get_current_wallpaper()).expanduser().resolve())

    elif path.startswith("@"):
        try:
            index = int(path[1:]) - 1
            if index < 0 or index >= len(favorites):
                raise IndexError(f"Invalid index: {index + 1}")

            removed = favorites.pop(index)
            CONFIG.set("favorites", favorites)
            log(f"Removed from favorites: {removed}", silent=silent)
            return
        except (ValueError, IndexError):
            log(f"Invalid index: {path}", silent=silent)
            return
    else:
        path = str(Path(path).expanduser().resolve())

    if path not in favorites:
        log("Not in favorites.", silent=silent)
        return

    favorites.remove(path)
    CONFIG.set("favorites", favorites)
    log(f"Removed from favorites: {path}", silent=silent)


@favorite_cmd.command("list")
@click.pass_context
def favorite_list_cmd(ctx):
    """
    List all favorite wallpapers.
    """
    silent = ctx.obj.get("silent")
    favorites = CONFIG.get("favorites", [])

    if not favorites:
        log("No favorites set.", silent=silent)
        return

    for idx, path in enumerate(favorites, start=1):
        log(f"{idx}: {path}", silent=silent)
