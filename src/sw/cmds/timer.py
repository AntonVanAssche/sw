#!/usr/bin/env python

import click

from sw.core.timer import TimerError, TimerManager
from sw.utils.common import err, log
from sw.utils.style import format_boolean, format_by_value, green


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
    try:
        tm = TimerManager()
        result = tm.enable()
        log(green(result), ctx)
    except TimerError as e:
        err("Failed to enable timer", e, ctx)
    except Exception as e:
        err("Unexpected error while enabling timer", e, ctx)


@timer_cmd.command("disable", short_help="Disable the timer")
@click.help_option("--help", "-h")
@click.pass_context
def timer_disable_cmd(ctx):
    """Disable the systemd timer for sw."""
    try:
        tm = TimerManager()
        result = tm.disable()
        log(green(result), ctx)
    except TimerError as e:
        err("Failed to disable timer", e, ctx)
    except Exception as e:
        err("Unexpected error while disabling timer", e, ctx)


@timer_cmd.command("toggle", short_help="Toggle the timer")
@click.help_option("--help", "-h")
@click.pass_context
def timer_toggle_cmd(ctx):
    """Toggle the systemd timer for sw."""
    try:
        tm = TimerManager()
        result = tm.toggle()
        log(green(result), ctx)
    except TimerError as e:
        err("Failed to toggle timer", e, ctx)
    except Exception as e:
        err("Unexpected error while toggling timer", e, ctx)


@timer_cmd.command("status", short_help="Get the timer status")
@click.help_option("--help", "-h")
@click.pass_context
def timer_status_cmd(ctx):
    """Show the current status of the sw systemd timer."""
    try:
        tm = TimerManager()

        active = tm.is_active()
        enabled = tm.is_enabled()
        time_left_str = tm.time_left()

        result_msgs = [
            f"Active: {format_boolean(active)}",
            f"Enabled: {format_boolean(enabled)}",
            f"Time left: {format_by_value(time_left_str, ("Timer is not active", "Timer expired recently"))}",
        ]

        log("\n".join(result_msgs), ctx)
    except TimerError as e:
        err("Failed to get timer status", e, ctx)
    except Exception as e:
        err("Unexpected error while checking timer status", e, ctx)
