#!/usr/bin/env python

import click

from sw.core.timer import TimerError, TimerManager
from sw.utils.common import err, log


# pylint: disable=unused-argument
@click.group("timer", short_help="Manage the sw systemd timer")
@click.help_option("--help", "-h")
@click.pass_context
def timer_cmd(ctx):
    """
    Manage the sw systemd timer.

    The timer is used to periodically change wallpapers automatically
    using a systemd timer unit. You can enable, disable, or check its status.
    """


@timer_cmd.command("enable", short_help="Enable the timer")
@click.help_option("--help", "-h")
@click.pass_context
def timer_enable_cmd(ctx):
    """Enable the systemd timer for sw."""
    silent = ctx.obj.get("silent", False)
    try:
        tm = TimerManager()
        result = tm.enable()
        log(result, silent=silent)
    except TimerError as e:
        err(ctx, "Failed to enable timer", e)
    except Exception as e:
        err(ctx, "Unexpected error while enabling timer", e)


@timer_cmd.command("disable", short_help="Disable the timer")
@click.help_option("--help", "-h")
@click.pass_context
def timer_disable_cmd(ctx):
    """Disable the systemd timer for sw."""
    silent = ctx.obj.get("silent", False)
    try:
        tm = TimerManager()
        result = tm.disable()
        log(result, silent=silent)
    except TimerError as e:
        err(ctx, "Failed to disable timer", e)
    except Exception as e:
        err(ctx, "Unexpected error while disabling timer", e)


@timer_cmd.command("toggle", short_help="Toggle the timer")
@click.help_option("--help", "-h")
@click.pass_context
def timer_toggle_cmd(ctx):
    """Toggle the systemd timer for sw."""
    silent = ctx.obj.get("silent", False)
    try:
        tm = TimerManager()
        result = tm.toggle()
        log(result, silent=silent)
    except TimerError as e:
        err(ctx, "Failed to toggle timer", e)
    except Exception as e:
        err(ctx, "Unexpected error while toggling timer", e)


@timer_cmd.command("status", short_help="Get the timer status")
@click.help_option("--help", "-h")
@click.pass_context
def timer_status_cmd(ctx):
    """Show the current status of the sw systemd timer."""
    silent = ctx.obj.get("silent", False)
    try:
        tm = TimerManager()

        result_msgs = [
            f"Active: {tm.is_active()}",
            f"Enabled: {tm.is_enabled()}",
            f"Time left: {tm.time_left()}",
        ]

        log("\n".join(result_msgs), silent=silent)
    except TimerError as e:
        err(ctx, "Failed to get timer status", e)
    except Exception as e:
        err(ctx, "Unexpected error while checking timer status", e)
