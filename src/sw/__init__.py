#!/usr/bin/env python

"""
sw - An overly complicated wallpaper switcher for Hyprland.
"""

__version__ = "1.2.0"

import json
import os
import shlex
import subprocess
import sys

import click

from sw.cmds.config import config_cmd
from sw.cmds.favorite import favorite_cmd
from sw.cmds.history import history_cmd
from sw.cmds.next import next_cmd
from sw.cmds.prev import prev_cmd
from sw.cmds.queue import queue_cmd
from sw.cmds.set import set_cmd
from sw.cmds.status import status_cmd
from sw.cmds.timer import timer_cmd
from sw.utils import style


# pylint: disable=no-value-for-parameter
@click.group()
@click.option("--silent", "-s", is_flag=True, help="Suppress output when necessary.")
@click.option(
    "--color",
    "-c",
    type=click.Choice(["auto", "never", "always"], case_sensitive=False),
    default="auto",
    help="Control colored output: auto, never, or always.",
)
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-v", help="Show the installed version of sw.")
@click.pass_context
def cli(ctx, silent, color):
    """sw - An overly complicated wallpaper switcher for Hyprland."""
    ctx.ensure_object(dict)
    ctx.obj["color"] = color
    ctx.obj["silent"] = silent

    style.set_color_mode(color)


cli.add_command(config_cmd, name="config")
cli.add_command(favorite_cmd, name="favorite")
cli.add_command(status_cmd, name="status")
cli.add_command(history_cmd, name="history")
cli.add_command(next_cmd, name="next")
cli.add_command(prev_cmd, name="prev")
cli.add_command(set_cmd, name="set")
cli.add_command(timer_cmd, name="timer")
cli.add_command(queue_cmd, name="queue")

if __name__ == "__main__":
    cli(obj={})
