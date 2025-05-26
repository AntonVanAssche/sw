#!/usr/bin/env python

from pathlib import Path
from typing import get_type_hints

import click

from sw.core.config import Config, ConfigError
from sw.utils.common import err, log
from sw.utils.style import cyan, format_json, green, red, yellow

CONFIG = Config()


def is_list_property(prop_name: str) -> bool:
    """Check if a config property returns a list."""
    prop = getattr(Config, prop_name, None)
    return isinstance(prop, property) and (
        get_type_hints(prop.fget).get("return") == list[Path] or get_type_hints(prop.fget).get("return") == list
    )


def parse_val(val: str) -> int | float | str:
    """Try to parse a string as int or float; fallback to stripped string."""
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val.strip()


def update_list_key(key: str, values: tuple[str], append: bool, remove: bool):
    current = CONFIG.get(key, [])
    if not isinstance(current, list):
        raise click.BadParameter(f"Key '{key}' is not a list")

    if append:
        new = list(dict.fromkeys(current + list(values)))
        CONFIG.set(key, new)
        return "append", key, values

    if remove:
        new = [v for v in current if v not in values]
        CONFIG.set(key, new)
        return "remove", key, values

    CONFIG.set(key, list(values))
    return "set", key, values


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
    try:
        value = CONFIG.get(key)
        if value is None:
            log(f"{cyan(key)}: {yellow('not set')}", ctx)
        else:
            if isinstance(value, list):
                colored_list = ", ".join(green(str(v)) for v in value)
                log(f"{cyan(key)}: [{colored_list}]", ctx)
            else:
                log(f"{cyan(key)}: {green(value)}", ctx)
    except (ConfigError, KeyError) as e:
        err(ctx, f"Error getting key '{key}'", e)
    except Exception as e:
        err(ctx, f"Unexpected error while getting key '{key}'", e)


@config_cmd.command("set")
@click.argument("key", required=True)
@click.argument("values", nargs=-1, required=True)
@click.option("--append", is_flag=True, help="Append value(s) to list-type key.")
@click.option("--remove", is_flag=True, help="Remove value(s) from list-type key.")
@click.pass_context
def set_config(ctx, key, values, append, remove):
    """
    Set a configuration key to a new value.

    Supports space-separated values for list-type keys (e.g. 'recency_exclude').
    Numeric values will be stored as numbers automatically.
    """
    silent = ctx.obj.get("silent")
    key = key.strip()

    try:
        if is_list_property(key):
            action, key, vals = update_list_key(key, values, append, remove)

            if action == "append":
                msg = f"Appended to '{cyan(key)}': {', '.join(green(v) for v in vals)}"
            elif action == "remove":
                msg = f"Removed from '{cyan(key)}': {', '.join(red(v) for v in vals)}"
            else:
                msg = f"Set '{cyan(key)}' to: {', '.join(green(v) for v in vals)}"

            log(msg, ctx)
        else:
            if append or remove:
                raise click.BadParameter(f"Key '{key}' does not support --append/--remove")

            if len(values) > 1:
                raise click.BadParameter(f"Key '{key}' only accepts a single value, but multiple were given.")

            val = parse_val(values[0])
            CONFIG.set(key, val)
            log(f"Set '{cyan(key)}' to: {green(val)}", ctx)
    except (ConfigError, click.BadParameter, KeyError) as e:
        err(ctx, f"Failed set key '{key}'", e)
    except Exception as e:
        err(ctx, "Unexpected error", e)


@config_cmd.command("unset")
@click.help_option("--help", "-h")
@click.argument("key", required=True)
@click.pass_context
def unset_config(ctx, key):
    """
    Unset a configuration key.

    This removes the specified key from the config file.
    """
    try:
        CONFIG.set(key, None)
        log(f"{cyan(key)}: {yellow('unset')}", ctx)
    except (ConfigError, KeyError) as e:
        err(ctx, f"Failed to unset key '{key}'", e)
    except Exception as e:
        err(ctx, "Unexpected error", e)


@config_cmd.command("show")
@click.help_option("--help", "-h")
@click.pass_context
def show_config(ctx):
    """
    Show all configuration settings.

    Displays the entire configuration as a formatted JSON object.
    """
    try:
        config_data = CONFIG.get_all()
        log(format_json(config_data), ctx)
    except Exception as e:
        err(ctx, "Failed to show configuration", e)
