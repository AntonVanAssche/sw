#!/usr/bin/env python

import click

from sw_cli import __version__
from sw_cli.cmds.config_cmd import config_cmd
from sw_cli.cmds.favorite_cmd import favorite_cmd
from sw_cli.cmds.history_cmd import history_cmd
from sw_cli.cmds.next_cmd import next_cmd
from sw_cli.cmds.prev_cmd import prev_cmd
from sw_cli.cmds.queue_cmd import queue_cmd
from sw_cli.cmds.set_cmd import set_cmd
from sw_cli.cmds.status_cmd import status_cmd
from sw_cli.cmds.timer_cmd import timer_cmd


@click.group()
@click.option("--silent", "-s", is_flag=True, help="Suppress output when necessary.")
@click.option(
    "--color",
    "-c",
    type=click.Choice(["auto", "never", "always"], case_sensitive=False),
    default="auto",
    help="Control colored output: auto, never, or always.",
)
@click.option("--notify", "-n", is_flag=True, help="Send notifications for actions.")
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-v", help="Show the installed version of sw.")
@click.pass_context
def cli(ctx, silent=False, color="auto", notify=False):
    """sw - An overly complicated wallpaper switcher for Hyprland."""
    ctx.ensure_object(dict)
    ctx.obj["color"] = color
    ctx.obj["notify"] = notify
    ctx.obj["silent"] = silent


cli.add_command(config_cmd)
cli.add_command(favorite_cmd)
cli.add_command(history_cmd)
cli.add_command(next_cmd)
cli.add_command(prev_cmd)
cli.add_command(queue_cmd)
cli.add_command(set_cmd)
cli.add_command(status_cmd)
cli.add_command(timer_cmd)
