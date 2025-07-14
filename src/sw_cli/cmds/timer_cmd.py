#!/usr/bin/env python

import click

from sw_cli.systemd import (
    DBusConnectionError,
    SystemdTimer,
    SystemdTimerActionError,
    SystemdTimerNotFoundError,
    SystemdTimerStatusError,
)
from sw_cli.utils import err, format_boolean, green, log, prettify_time


@click.group("timer", short_help="Manage the sw systemd timer")
@click.help_option("--help", "-h")
def timer_cmd():
    """
    Manage the sw systemd timer.

    The timer is used to periodically change wallpapers automatically
    using a systemd timer unit. You can enable, disable, start, stop, or check its status.
    """


@timer_cmd.command("enable", short_help="Enable the timer unit")
@click.option("--now", is_flag=True, help="Also start the timer immediately")
@click.help_option("--help", "-h")
@click.pass_context
def timer_enable_cmd(ctx, now):
    """Enable the systemd timer unit."""
    try:
        tm = SystemdTimer()

        tm.enable()
        log(green("Timer unit enabled."), ctx)

        if now:
            tm.start()
            log(green("Timer unit started (--now)."), ctx)
    except DBusConnectionError as e:
        err("Failed to connect to D-Bus session", e, ctx)
    except SystemdTimerNotFoundError as e:
        err("Timer unit not found", e, ctx)
    except (SystemdTimerActionError, SystemdTimerStatusError) as e:
        err("Failed to enable timer", e, ctx)
    except Exception as e:
        err("Unexpected error while enabling timer", e, ctx)


@timer_cmd.command("disable", short_help="Disable the timer unit")
@click.option("--now", is_flag=True, help="Also stop the timer immediately")
@click.help_option("--help", "-h")
@click.pass_context
def timer_disable_cmd(ctx, now):
    """Disable the systemd timer unit."""
    try:
        tm = SystemdTimer()

        tm.disable()
        log(green("Timer unit disabled."), ctx)

        if now:
            tm.stop()
            log(green("Timer unit stopped (--now)."), ctx)
    except DBusConnectionError as e:
        err("Failed to connect to D-Bus session", e, ctx)
    except SystemdTimerNotFoundError as e:
        err("Timer unit not found", e, ctx)
    except (SystemdTimerActionError, SystemdTimerStatusError) as e:
        err("Failed to disable timer", e, ctx)
    except Exception as e:
        err("Unexpected error while disabling timer", e, ctx)


@timer_cmd.command("start", short_help="Start the timer unit now")
@click.help_option("--help", "-h")
@click.pass_context
def timer_start_cmd(ctx):
    """Start the systemd timer unit immediately."""
    try:
        tm = SystemdTimer()

        tm.start()
        log(green("Timer unit started."), ctx)
    except DBusConnectionError as e:
        err("Failed to connect to D-Bus session", e, ctx)
    except SystemdTimerNotFoundError as e:
        err("Timer unit not found", e, ctx)
    except (SystemdTimerActionError, SystemdTimerStatusError) as e:
        err("Failed to start timer", e, ctx)
    except Exception as e:
        err("Unexpected error while starting timer", e, ctx)


@timer_cmd.command("stop", short_help="Stop the timer unit")
@click.help_option("--help", "-h")
@click.pass_context
def timer_stop_cmd(ctx):
    """Stop the systemd timer unit immediately."""
    try:
        tm = SystemdTimer()

        tm.stop()
        log(green("Timer unit stopped."), ctx)
    except DBusConnectionError as e:
        err("Failed to connect to D-Bus session", e, ctx)
    except SystemdTimerNotFoundError as e:
        err("Timer unit not found", e, ctx)
    except (SystemdTimerActionError, SystemdTimerStatusError) as e:
        err("Failed to stop timer", e, ctx)
    except Exception as e:
        err("Unexpected error while stopping timer", e, ctx)


@timer_cmd.command("status", short_help="Show timer unit status")
@click.help_option("--help", "-h")
@click.pass_context
def timer_status_cmd(ctx):
    """Show the current status of the systemd timer unit."""
    try:
        tm = SystemdTimer()

        status = tm.get_status()
        is_active = status.get("ActiveState") == "active"
        is_enabled = status.get("SubState") == "enabled"

        if is_active:
            next_elapse = prettify_time(status.get("NextElapse"))
        else:
            next_elapse = "N/A"

        result_msgs = [
            f"Active:      {format_boolean(is_active)}",
            f"Enabled:     {format_boolean(is_enabled)}",
            f"Next elapse: {next_elapse}",
        ]

        log("\n".join(result_msgs), ctx)

    except DBusConnectionError as e:
        err("Failed to connect to D-Bus session", e, ctx)
    except SystemdTimerNotFoundError as e:
        err("Timer unit not found", e, ctx)
    except (SystemdTimerActionError, SystemdTimerStatusError) as e:
        err("Failed to get timer status", e, ctx)
    except Exception as e:
        err("Unexpected error while getting timer status", e, ctx)
