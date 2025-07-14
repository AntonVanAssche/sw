#!/usr/bin/env python

import random

import click

from sw_cli.queue import QueueError, QueueManager, QueueNotFoundError, QueueReadError, QueueWriteError
from sw_cli.utils import err, green, log, red, warn, yellow
from sw_lib.config import Config, ConfigError, ConfigLoadError, ConfigValidationError


def handle_error(ctx, message, exception):
    err(message, exception, ctx)


@click.group("queue", short_help="Manage the wallpaper queue")
@click.help_option("--help", "-h")
def queue_cmd():
    """Manage the wallpaper queue."""


@queue_cmd.command("add")
@click.help_option("--help", "-h")
@click.argument("paths", nargs=-1, required=True)
@click.option("--shuffle", "-s", is_flag=True, help="Shuffle the new entries before adding.")
@click.pass_context
def add_cmd(ctx, paths, shuffle):
    """Add wallpapers to the queue."""
    try:
        config = Config()
        qm = QueueManager(config.queue_file)

        new_entries = list(paths)

        if shuffle:
            random.shuffle(new_entries)

        qm.add(new_entries)
        log(f"Added {green(len(new_entries))} file(s) to the queue.", ctx)
    except (ConfigLoadError, ConfigValidationError, ConfigError) as e:
        err("Failed to load configuration", e, ctx)
    except (QueueNotFoundError, QueueReadError, QueueWriteError) as e:
        handle_error(ctx, "Queue file error while adding entries", e)
        err("Failed to add entries to the queue.", e, ctx)
    except Exception as e:
        err("Unexpected error while adding entries to the queue.", e, ctx)


@queue_cmd.command("rm")
@click.help_option("--help", "-h")
@click.argument("paths", nargs=-1, required=True)
@click.pass_context
def rm_cmd(ctx, paths):
    """Remove wallpapers from the queue."""
    try:
        config = Config()
        qm = QueueManager(config.queue_file)

        before = qm.get()
        qm.remove(paths)
        after = qm.get()
        removed_count = len(before) - len(after)

        if removed_count == 0:
            warn("No matching entries found to remove.", ctx)
        else:
            log(f"Removed {red(removed_count)} file(s) from the queue.", ctx)
    except (ConfigLoadError, ConfigValidationError, ConfigError) as e:
        err("Failed to load configuration", e, ctx)
    except (QueueNotFoundError, QueueReadError, QueueWriteError) as e:
        err("Failed to remove entries from the queue.", e, ctx)
    except Exception as e:
        err("Unexpected error while removing entries from the queue.", e, ctx)


@queue_cmd.command("list")
@click.help_option("--help", "-h")
@click.pass_context
def list_cmd(ctx):
    """
    List all wallpapers currently in the queue.
    """
    try:
        config = Config()
        qm = QueueManager(config.queue_file)

        entries = qm.get()

        if entries:
            for i, path in enumerate(entries, start=1):
                log(f"{yellow(i)}: {green(path)}", ctx)
        else:
            warn("No wallpapers in the queue.", ctx)
    except (ConfigLoadError, ConfigValidationError, ConfigError) as e:
        err("Failed to load configuration", e, ctx)
    except (QueueNotFoundError, QueueReadError) as e:
        err("Failed to read queue entries.", e, ctx)
    except QueueError as e:
        err("Failed to list entries in the queue.", e, ctx)
    except Exception as e:
        err("Unexpected error while listing entries in the queue.", e, ctx)


@queue_cmd.command("empty")
@click.help_option("--help", "-h")
@click.pass_context
def empty_cmd(ctx):
    """Clear all wallpapers from the queue."""
    try:
        config = Config()
        qm = QueueManager(config.queue_file)

        qm.clear()
        log("Queue emptied.", ctx)
    except (ConfigLoadError, ConfigValidationError, ConfigError) as e:
        err("Failed to load configuration", e, ctx)
    except (QueueWriteError,) as e:
        err("Failed to empty the queue.", e, ctx)
    except QueueError as e:
        err("Failed to empty the queue due to a queue error.", e, ctx)
    except Exception as e:
        err("Unexpected error while emptying the queue.", e, ctx)


@queue_cmd.command("shuffle")
@click.help_option("--help", "-h")
@click.pass_context
def shuffle_cmd(ctx):
    """Randomly shuffle the queue order."""
    try:
        config = Config()
        qm = QueueManager(config.queue_file)
        entries = qm.get()

        if entries:
            qm.shuffle()
            log("Queue shuffled.", ctx)
        else:
            warn("Queue is empty, nothing to shuffle.", ctx)
    except (ConfigLoadError, ConfigValidationError, ConfigError) as e:
        err("Failed to load configuration", e, ctx)
    except (QueueNotFoundError, QueueReadError, QueueWriteError) as e:
        err("Failed to shuffle entries in the queue.", e, ctx)
    except QueueError as e:
        err("Failed to shuffle entries in the queue.", e, ctx)
    except Exception as e:
        err("Unexpected error while shuffling entries in the queue.", e, ctx)
