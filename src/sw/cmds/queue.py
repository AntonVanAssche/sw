#!/usr/bin/env python

import click

from sw.core.queue import InvalidPatternError, QueueEmptyError, QueueError, QueueManager
from sw.utils.common import err, log, warn
from sw.utils.style import green, red, yellow


# pylint: disable=unused-argument
@click.group("queue", short_help="Manage the wallpaper queue")
@click.help_option("--help", "-h")
@click.pass_context
def queue_cmd(ctx):
    """
    Manage the wallpaper queue.

    The queue determines which wallpapers are set in order when running 'sw set'
    without a specific path.
    """


@queue_cmd.command("add")
@click.help_option("--help", "-h")
@click.argument("patterns", nargs=-1, required=True)
@click.option("--shuffle", "-s", is_flag=True, help="Shuffle the queue entries before adding.")
@click.pass_context
def add_cmd(ctx, patterns, shuffle):
    """
    Add wallpapers to the queue using glob patterns.

    Accepts one or more file paths or glob patterns to add matching wallpapers
    to the queue. Directories are not allowed unless expanded via glob.
    """
    qm = QueueManager()
    try:
        count = qm.add(patterns, shuffle=shuffle)
        log(f"Added {green(count)} file(s) to the queue.", ctx)
    except InvalidPatternError as e:
        err("Invalid pattern provided", e, ctx)
    except QueueError as e:
        err("Failed to add entries", e, ctx)
    except Exception as e:
        err("Unexpected error while adding entries", e, ctx)


@queue_cmd.command("rm")
@click.help_option("--help", "-h")
@click.argument("patterns", nargs=-1, required=True)
@click.pass_context
def rm_cmd(ctx, patterns):
    """
    Remove wallpapers from the queue using glob patterns.

    Patterns can include full file paths or wildcards. Matching entries
    will be removed from the queue.
    """
    qm = QueueManager()
    try:
        count = qm.rm(patterns)
        if count == 0:
            warn("No matching entries found to remove.", ctx)
        else:
            log(f"Removed {red(count)} file(s) from the queue.", ctx)
    except InvalidPatternError as e:
        err("Invalid pattern provided", e, ctx)
    except QueueError as e:
        err("Failed to remove entries", e, ctx)
    except Exception as e:
        err("Unexpected error while removing entries", e, ctx)


@queue_cmd.command("list")
@click.help_option("--help", "-h")
@click.pass_context
def list_cmd(ctx):
    """
    List all wallpapers currently in the queue.

    If the queue is empty, an informative message will be printed.
    """
    qm = QueueManager()

    try:
        entries = qm.list()
        for entry in enumerate(entries, start=1):
            log(f"{yellow(entry[0])}: {green(entry[1])}", ctx)
    except QueueEmptyError:
        warn("No wallpapers in the queue.", ctx)
    except QueueError as e:
        err("Failed to list queue entries", e, ctx)
    except Exception as e:
        err("Unexpected error while listing queue", e, ctx)


@queue_cmd.command("empty")
@click.help_option("--help", "-h")
@click.pass_context
def empty_cmd(ctx):
    """
    Clear all wallpapers from the queue.

    This cannot be undone.
    """
    qm = QueueManager()

    try:
        qm.empty()
        log("Queue emptied.", ctx)
    except QueueError as e:
        err("Failed to empty queue", e, ctx)
    except Exception as e:
        err("Unexpected error while emptying queue", e, ctx)


@queue_cmd.command("shuffle")
@click.help_option("--help", "-h")
@click.pass_context
def shuffle_cmd(ctx):
    """
    Randomly shuffle the order of wallpapers in the queue.

    This does not add or remove wallpapers—only changes their order.
    """
    qm = QueueManager()
    try:
        qm.shuffle()
        log("Queue shuffled.", ctx)
    except QueueEmptyError:
        warn("Queue is empty, nothing to shuffle.", ctx)
    except QueueError as e:
        err("Failed to shuffle queue", e, ctx)
    except Exception as e:
        err("Unexpected error while shuffling queue", e, ctx)
