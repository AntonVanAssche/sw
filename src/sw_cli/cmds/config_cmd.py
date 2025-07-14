#!/usr/bin/env python

import click

from sw_cli.utils import cyan, err, format_json, green, log, red, yellow
from sw_lib.config import Config, ConfigError, ConfigKeyError, ConfigLoadError, ConfigValidationError, ConfigWriteError


def is_list_property(config: Config, key: str) -> bool:
    """Check if a config key path points to a list-type value."""
    value = config.get(key, None)
    return isinstance(value, list)


def parse_val(val: str) -> int | float | str:
    """Try to parse a string as int or float; fallback to stripped string."""
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val.strip()


def update_list_key(config: Config, key: str, values: tuple[str], append: bool, remove: bool):
    """Update a list-type config key by appending, removing, or setting new values."""
    current = config.get(key, [])
    if not isinstance(current, list):
        raise click.BadParameter(f"Key '{key}' is not a list")

    if append:
        new = list(dict.fromkeys(current + list(values)))
        config.set(key, new)
        return "append", key, values

    if remove:
        new = [v for v in current if v not in values]
        config.set(key, new)
        return "remove", key, values

    config.set(key, list(values))
    return "set", key, values


@click.group("config", short_help="Manage the configuration of sw")
@click.help_option("--help", "-h")
def config_cmd():
    """
    Manage the configuration of sw.

    This allows you to view, set, or unset configuration keys that affect
    the behavior of sw.
    """


@config_cmd.command("get")
@click.help_option("--help", "-h")
@click.argument("key", required=True)
@click.pass_context
def get_config(ctx, key):
    """Get the current value of a configuration key."""
    try:
        config = Config()
        value = config.get(key)
        if value is None:
            log(f"{cyan(key)}: {yellow('not set')}", ctx)
        else:
            if isinstance(value, list):
                colored_list = ", ".join(green(str(v)) for v in value)
                log(f"{cyan(key)}: [{colored_list}]", ctx)
            else:
                log(f"{cyan(key)}: {green(value)}", ctx)
    except (ConfigLoadError, ConfigValidationError, ConfigError, ConfigKeyError) as e:
        err(f"Error getting key '{key}'", e, ctx)
    except Exception as e:
        err(f"Unexpected error while getting key '{key}'", e, ctx)


@config_cmd.command("set")
@click.help_option("--help", "-h")
@click.argument("key", required=True)
@click.argument("values", nargs=-1, required=True)
@click.option("--append", is_flag=True, help="Append value(s) to list-type key.")
@click.option("--remove", is_flag=True, help="Remove value(s) from list-type key.")
@click.pass_context
def set_config_cmd(ctx, key, values, append, remove):
    """Set a configuration key to a new value."""
    key = key.strip()

    try:
        config = Config()

        if is_list_property(config, key):
            action, key, vals = update_list_key(config, key, values, append, remove)

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
            config.set(key, val)
            log(f"Set '{cyan(key)}' to: {green(val)}", ctx)
    except (ConfigLoadError, ConfigValidationError) as e:
        err("Failed to load configuration", e, ctx)
    except ConfigWriteError as e:
        err("Failed to write to configuration.", e, ctx)
    except ConfigError as e:
        err("Configuration error.", e, ctx)
    except Exception as e:
        err("Unexpected error", e, ctx)


@config_cmd.command("unset")
@click.help_option("--help", "-h")
@click.argument("key", required=True)
@click.pass_context
def unset_config_cmd(ctx, key):
    """Unset a configuration key."""
    try:
        config = Config()

        config.unset(key)
        log(f"{cyan(key)}: {yellow('unset')}", ctx)
    except (ConfigLoadError, ConfigValidationError) as e:
        err("Failed to load configuration", e, ctx)
    except ConfigWriteError as e:
        err("Failed to write to configuration.", e, ctx)
    except ConfigError as e:
        err("Configuration error.", e, ctx)
    except Exception as e:
        err("Unexpected error", e, ctx)


@config_cmd.command("show")
@click.help_option("--help", "-h")
@click.pass_context
def show_config(ctx):
    """Show all configuration settings."""
    try:
        config = Config()
        config_data = config.get_all()
        log(format_json(config_data), ctx)
    except (ConfigLoadError, ConfigValidationError, ConfigError) as e:
        err("Failed to load configuration", e, ctx)
    except Exception as e:
        err("Unexpected error while showing configuration", e, ctx)
