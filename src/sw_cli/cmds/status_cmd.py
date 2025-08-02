#!/usr/bin/env python

from pathlib import Path

import click

from sw_cli.systemd import (
    DBusConnectionError,
    SystemdTimer,
    SystemdTimerActionError,
    SystemdTimerNotFoundError,
    SystemdTimerStatusError,
)
from sw_cli.utils import err, format_boolean, green, log, prettify_path, prettify_time, yellow
from sw_lib.config import Config, ConfigError, ConfigLoadError, ConfigValidationError
from sw_lib.history import HistoryEntryNotFoundError, HistoryManager


def get_wallpaper_info(config):
    hm = HistoryManager(config.history_file)
    return hm.get(-1)


def format_fields(wallpaper_info, timer, options):
    fields = []

    if options.get("name"):
        fields.append(("Name", green(prettify_path(wallpaper_info.path))))
    if not options.get("hide_path"):
        fields.append(("Path", green(wallpaper_info.path)))
    if options.get("directory"):
        fields.append(("Directory", green(str(Path(wallpaper_info.path).parent))))

    if timer and not options.get("hide_timer"):
        is_active = timer.is_active()
        is_enabled = timer.is_enabled()
        next_elapse = timer.next_elapse_mono() if is_active else None

        next_elapse_str = prettify_time(next_elapse) if next_elapse else yellow("N/A")

        fields.append(("Active", format_boolean(is_active)))
        fields.append(("Enabled", format_boolean(is_enabled)))
        fields.append(("Next elapse", green(next_elapse_str)))

    return fields


@click.command("status", short_help="Show current wallpaper status")
@click.help_option("--help", "-h")
@click.option("-n", "--name", is_flag=True, help="Show the pretty name of the current wallpaper")
@click.option("-d", "--directory", is_flag=True, help="Show the directory of the current wallpaper")
@click.option("-P", "--hide-path", is_flag=True, help="Hide the path of the current wallpaper")
@click.option("-T", "--hide-timer", is_flag=True, help="Hide the timer information")
@click.pass_context
def status_cmd(ctx, name, directory, hide_path, hide_timer):
    """Show the current wallpaper status."""
    try:
        config = Config()
        wallpaper_info = get_wallpaper_info(config)

        timer = SystemdTimer() if not hide_timer else None

        options = {
            "name": name,
            "directory": directory,
            "hide_path": hide_path,
            "hide_timer": hide_timer,
        }

        fields = format_fields(wallpaper_info, timer, options)

        if not fields:
            log("No wallpaper currently set.", ctx)
        else:
            max_label_len = max(len(label) for label, _ in fields)
            parts = [f"{label+':':<{max_label_len+1}} {value}" for label, value in fields]
            log("\n".join(parts), ctx)
    except (ConfigError, ConfigLoadError, ConfigValidationError) as e:
        err("Failed to load config", e, ctx)
    except HistoryEntryNotFoundError as e:
        err("Failed to read current wallpaper from history", e, ctx)
    except (DBusConnectionError, SystemdTimerNotFoundError, SystemdTimerActionError, SystemdTimerStatusError) as e:
        err("Failed to get timer info", e, ctx)
    except Exception as e:
        err("Unexpected error occurred", e, ctx)
