#!/usr/bin/env python

import random

import click

from sw_cli.history import HistoryEntryError, HistoryManager
from sw_cli.ipc import SWDaemonError
from sw_cli.queue import QueueManager
from sw_cli.utils import err, green, log, resolve_indexed_path
from sw_cli.wallpaper import WallpaperApplier, WallpaperApplyError, WallpaperNotFoundError, WallpaperSelector
from sw_lib.config import Config, ConfigError, ConfigLoadError, ConfigValidationError


@click.command("set", short_help="Set a wallpaper")
@click.help_option("--help", "-h")
@click.option("-f", "--favorite", metavar="PATH_OR_@INDEX", help="Set wallpaper from favorites list")
@click.option("-d", "--use-dir", is_flag=True, help="Pick from the directory of current wallpaper")
@click.argument("path", required=False)
@click.pass_context
def set_cmd(ctx, favorite, use_dir, path):
    """
    Set a wallpaper.

    You can specify:

    - A direct path to an image
    - A directory to pick from
    - A favorite/history index with '@N'
    - Or nothing, to pick randomly
    """
    try:
        config = Config()
        qm = QueueManager(config.queue_file)
        hm = HistoryManager(
            config.history_file,
            config.history_limit,
            config.recency_timeout,
        )
        selector = WallpaperSelector(config, qm, hm)
        applier = WallpaperApplier(hm)

        final_path = None

        if favorite is not None:
            if favorite.startswith("@"):
                final_path = resolve_indexed_path(favorite, config.favorites)
            else:
                final_path = random.choice(config.favorites)
        elif path is not None and path.startswith("@"):
            final_path = resolve_indexed_path(path, [entry.path for entry in hm.get()])
        else:
            final_path = path

        entry = selector.select_wallpaper(path=final_path, use_dir=use_dir)
        if not entry:
            err("No wallpaper selected", "Nothing matched the selection criteria", ctx)

        applier.apply(entry)
        log(f"Wallpaper set: {green(entry)}", ctx)
    except (ConfigLoadError, ConfigValidationError, ConfigError) as e:
        err("Failed to load configuration", e, ctx)
    except (WallpaperNotFoundError, WallpaperApplyError, SWDaemonError) as e:
        err("Failed to set wallpaper", e, ctx)
    except (HistoryEntryError, ValueError, IndexError) as e:
        err("Error resolving wallpaper path from history", e, ctx)
    except Exception as e:
        err("Unexpected error", e, ctx)
