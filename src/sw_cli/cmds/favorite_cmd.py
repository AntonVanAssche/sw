#!/usr/bin/env python

from pathlib import Path

import click

from sw_cli.history import HistoryEntryNotFoundError, HistoryError, HistoryManager
from sw_cli.utils import cyan, err, green, log, red, resolve_indexed_path, warn, yellow
from sw_lib.config import Config, ConfigError, ConfigLoadError, ConfigValidationError, ConfigWriteError


@click.group("favorite", short_help="Manage favorite wallpapers")
@click.help_option("--help", "-h")
def favorite_cmd():
    """
    Manage your favorite wallpapers.

    This command allows you to add, remove, and list wallpapers in your
    favorites.
    """


@favorite_cmd.command("add")
@click.help_option("--help", "-h")
@click.argument("path", required=False)
@click.pass_context
def favorite_add_cmd(ctx, path):
    """
    Add a wallpaper to your favorites.

    You can specify:

    - A direct path to an image
    - A history index with '@N'
    """
    try:
        config = Config()
        favorites = list(map(str, config.favorites))
        hm = HistoryManager(config.history_file)

        if not favorites:
            warn("No favorites to remove.", ctx)
            return

        if path:
            if path.startswith("@"):
                path = resolve_indexed_path(path, hm.get()).path
        else:
            path = hm.get(-1).path

        path = str(Path(path).expanduser().resolve())

        if path in favorites:
            warn("Already in favorites.", ctx)
        else:
            favorites.append(path)
            config.set("wallpaper.favorites", favorites)
            log(f"Added to {cyan('favorites')}: {green(path)}", ctx)
    except (ConfigLoadError, ConfigValidationError) as e:
        err("Failed to load configuration", e, ctx)
    except ConfigWriteError as e:
        err("Failed to write to configuration.", e, ctx)
    except ConfigError as e:
        err("Configuration error.", e, ctx)
    except (HistoryEntryNotFoundError, HistoryError) as e:
        err("Failed to get current wallpaper from history", e, ctx)
    except Exception as e:
        err(red("Unexpected error"), e, ctx)


@favorite_cmd.command("rm")
@click.help_option("--help", "-h")
@click.argument("path", required=False)
@click.pass_context
def favorite_rm_cmd(ctx, path):
    """
    Remove a wallpaper from your favorites.

    You can specify:

    - A direct path to an image
    - A favorite index with '@N'
    """
    try:
        config = Config()
        favorites = list(map(str, config.favorites))
        hm = HistoryManager(config.history_file)

        if not favorites:
            warn("No favorites to remove.", ctx)
            return

        if path:
            if path.startswith("@"):
                path = resolve_indexed_path(path, favorites)
        else:
            path = hm.get(-1).path

        path = str(Path(path).expanduser().resolve())

        if path in favorites:
            favorites.remove(path)
            config.set("wallpaper.favorites", favorites)
            log(f"Removed from {cyan('favorites')}: {red(path)}", ctx)
        else:
            warn("Not in favorites.", ctx)
    except IndexError as e:
        err(f"Invalid index provided: {e}", ctx)
    except (ConfigLoadError, ConfigValidationError) as e:
        err("Failed to load configuration", e, ctx)
    except ConfigWriteError as e:
        err("Failed to write to configuration.", e, ctx)
    except ConfigError as e:
        err("Configuration error.", e, ctx)
    except (HistoryEntryNotFoundError, HistoryError) as e:
        err("Failed to get current wallpaper from history", e, ctx)
    except Exception as e:
        err(red("Unexpected error"), e, ctx)


@favorite_cmd.command("list")
@click.help_option("--help", "-h")
@click.pass_context
def favorite_list_cmd(ctx):
    """
    List all favorite wallpapers.
    """
    try:
        config = Config()
        favorites = list(map(str, config.favorites))

        if not favorites:
            warn("No favorites found.", ctx)
            return

        for idx, path in enumerate(favorites, start=1):
            log(f"{yellow(str(idx))}: {green(path)}", ctx)

    except (ConfigLoadError, ConfigValidationError, ConfigError) as e:
        err("Failed to load configuration", e, ctx)
    except Exception as e:
        err(red("Unexpected error while listing favorites."), e, ctx)
