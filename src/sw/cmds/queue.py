#!/usr/bin/env python

import click

from sw.core.queue import QueueManager
from sw.utils.common import log


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
    qm.add(patterns, shuffle=shuffle)
    log(f"Added the following files to the queue: \n{'\n'.join(patterns)}", silent=ctx.obj["silent"])


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
    qm.rm(patterns)
    log(f"Removed the following files from the queue: \n{'\n'.join(patterns)}", silent=ctx.obj["silent"])


@queue_cmd.command("list")
@click.help_option("--help", "-h")
def list_cmd():
    """
    List all wallpapers currently in the queue.

    If the queue is empty, an informative message will be printed.
    """
    qm = QueueManager()
    entries = qm.list()
    if not entries:
        log("Queue is empty.", silent=False)
    else:
        for entry in entries:
            log(entry, silent=False)


@queue_cmd.command("empty")
@click.help_option("--help", "-h")
@click.pass_context
def empty_cmd(ctx):
    """
    Clear all wallpapers from the queue.

    This cannot be undone.
    """
    qm = QueueManager()
    qm.empty()
    log("Queue emptied.", silent=ctx.obj["silent"])


@queue_cmd.command("shuffle")
@click.help_option("--help", "-h")
@click.pass_context
def shuffle_cmd(ctx):
    """
    Randomly shuffle the order of wallpapers in the queue.

    This does not add or remove wallpapers—only changes their order.
    """
    qm = QueueManager()
    qm.shuffle()
    log("Queue shuffled.", silent=ctx.obj["silent"])
