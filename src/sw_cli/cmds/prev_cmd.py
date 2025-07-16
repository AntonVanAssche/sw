#!/usr/bin/env python

import click

from sw_cli.ipc import SWDaemonError
from sw_cli.utils import err, green, log
from sw_cli.wallpaper import WallpaperApplier, WallpaperApplyError, WallpaperNotFoundError
from sw_lib.config import Config, ConfigError, ConfigLoadError, ConfigValidationError
from sw_lib.history import HistoryEntryNotFoundError, HistoryManager


@click.command("prev", short_help="Set the previous wallpaper")
@click.help_option("--help", "-h")
@click.pass_context
def prev_cmd(ctx):
    """Set the previous wallpaper"""
    try:
        config = Config()
        hm = HistoryManager(
            config.history_file,
            config.history_limit,
            config.recency_timeout,
        )
        applier = WallpaperApplier(hm)

        if hm.is_empty():
            err("History is empty", "No previous wallpaper to apply", ctx)

        entry = hm.get(-2)

        if entry is None:
            err("No previous wallpaper found", "History might be empty or corrupted", ctx)

        if not entry.path:
            err("Previous wallpaper path is empty", "Cannot apply an empty path", ctx)

        applier.apply(entry.path)
        log(f"Wallpaper set: {green(entry.path)}", ctx)
    except (ConfigLoadError, ConfigValidationError, ConfigError) as e:
        err("Failed to load configuration", e, ctx)
    except (WallpaperNotFoundError, WallpaperApplyError, SWDaemonError) as e:
        err("Failed to set wallpaper", e, ctx)
    except (HistoryEntryNotFoundError, ValueError, IndexError) as e:
        err("Error resolving wallpaper path from history", e, ctx)
    except Exception as e:
        err("Unexpected error", e, ctx)
