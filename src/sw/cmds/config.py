#!/usr/bin/env python

import json

import click

from sw.core.config import Config
from sw.utils.common import log

CONFIG = Config()


# pylint: disable=unused-argument
@click.group("config", short_help="Manage the configuration of sw")
@click.help_option("--help", "-h")
@click.pass_context
def config_cmd(ctx):
    """
    Manage the configuration of sw.

    This allows you to view, set, or unset configuration keys that affect
    the behavior of the wallpaper switcher.
    """


@config_cmd.command("get")
@click.help_option("--help", "-h")
@click.argument("key", required=True)
@click.pass_context
def get_config(ctx, key):
    """
    Get the current value of a configuration key.
    """
    value = CONFIG.get(key)
    if value is None:
        log(f"{key}: not set", silent=ctx.obj.get("silent"))
    else:
        log(f"{key}: {value}", silent=ctx.obj.get("silent"))


@config_cmd.command("set")
@click.help_option("--help", "-h")
@click.argument("key", nargs=1, required=True)
@click.argument("value", nargs=-1, required=True)
@click.pass_context
def set_config(ctx, key, value):
    """
    Set a configuration key to a new value.

    Supports space-separated values for list-type keys (e.g. 'recency_exclude').
    Numeric values will be stored as numbers automatically.
    """
    list_keys = {"recency_exclude"}
    silent = ctx.obj.get("silent")
    key = key.strip()

    def parse_val(val):
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val.strip()

    if key in list_keys:
        formatted_value = [parse_val(v) for v in value]
    elif len(value) > 1:
        raise click.BadParameter(f"Key '{key}' only accepts a single value, but multiple were given.")
    else:
        formatted_value = parse_val(value[0])

    try:
        CONFIG.set(key, formatted_value)
        log(f"Set '{key}' to: {formatted_value}", silent=silent)
    except Exception as e:
        log(f"Failed to set config: {e}", silent=silent)


@config_cmd.command("unset")
@click.help_option("--help", "-h")
@click.argument("key", required=True)
@click.pass_context
def unset_config(ctx, key):
    """
    Unset a configuration key.

    This removes the specified key from the config file.
    """
    CONFIG.set(key, None)
    log(f"{key}: unset", silent=ctx.obj.get("silent"))


@config_cmd.command("show")
@click.help_option("--help", "-h")
@click.pass_context
def show_config(ctx):
    """
    Show all configuration settings.

    Displays the entire configuration as a formatted JSON object.
    """
    config_data = CONFIG.get_all()
    log(json.dumps(config_data, indent=2), silent=ctx.obj.get("silent"))
