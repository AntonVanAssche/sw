#!/usr/bin/env python

import click

from sw.core.timer import TimerManager
from sw.utils.common import log


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
    """
    Enable the systemd timer for sw.

    This starts and enables the timer unit so that wallpapers change
    at regular intervals based on your systemd configuration.
    """
    tm = TimerManager()
    result = tm.enable()
    log(result, silent=ctx.obj.get("silent", False))


@timer_cmd.command("disable", short_help="Disable the timer")
@click.help_option("--help", "-h")
@click.pass_context
def timer_disable_cmd(ctx):
    """
    Disable the systemd timer for sw.

    This stops and disables the timer, preventing automatic wallpaper changes.
    """
    tm = TimerManager()
    result = tm.disable()
    log(result, silent=ctx.obj.get("silent", False))


@timer_cmd.command("toggle", short_help="Start the timer")
@click.help_option("--help", "-h")
@click.pass_context
def timer_toggle_cmd(ctx):
    """
    Toggle the systemd timer for sw.
    This command will start the timer if it is currently inactive,
    or stop it if it is currently active.
    """
    tm = TimerManager()
    result = tm.toggle()
    log(result, silent=ctx.obj.get("silent", False))


@timer_cmd.command("status", short_help="Get the timer status")
@click.help_option("--help", "-h")
@click.pass_context
def timer_status_cmd(ctx):
    """
    Show the current status of the sw systemd timer.

    Displays whether the timer is currently active, whether it's enabled,
    and how much time is left until the next activation.
    """
    silent = ctx.obj.get("silent", False)
    tm = TimerManager()

    result_msgs = []
    result_msgs.append(f"Active: {tm.is_active()}")
    result_msgs.append(f"Enabled: {tm.is_enabled()}")
    result_msgs.append(f"Time left: {tm.time_left()}")

    log("\n".join(result_msgs), silent=silent)
