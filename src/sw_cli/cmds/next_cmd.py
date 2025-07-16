#!/usr/bin/env python

import click

from sw_cli.ipc import SWDaemonError
from sw_cli.queue import QueueManager
from sw_cli.utils import err, green, log
from sw_cli.wallpaper import WallpaperApplier, WallpaperApplyError, WallpaperNotFoundError, WallpaperSelector
from sw_lib.config import Config, ConfigError, ConfigLoadError, ConfigValidationError
from sw_lib.history import HistoryEntryError, HistoryManager


@click.command("next", short_help="Set the next wallpaper")
@click.help_option("--help", "-h")
@click.pass_context
def next_cmd(ctx):
    """
    Set the next wallpaper

    The following precedence is used to select the next wallpaper:

    - First entry in the queue
    - Random from the default directory
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

        entry = selector.select_wallpaper(path=None, use_dir=False)

        if entry is None:
            err("No wallpaper selected", "No valid wallpaper found", ctx)

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
