#!/usr/bin/env python

import time

import click

from sw.core.history import HistoryManager
from sw.utils.common import err, log


# pylint: disable=unused-argument
@click.group("history", short_help="Manage wallpaper history")
@click.help_option("--help", "-h")
@click.pass_context
def history_cmd(ctx):
    """
    Manage the wallpaper history.

    Provides utilities to list and remove previously set wallpapers.
    """


@history_cmd.command("list", short_help="List wallpaper history entries")
@click.help_option("--help", "-h")
@click.option("-n", "--lines", type=int, default=None, help="Show only the last N entries")
@click.option("-u", "--unique", is_flag=True, help="Show only unique entries (remove duplicates)")
@click.pass_context
def history_list_cmd(ctx, lines, unique):
    """
    List entries in the wallpaper history.

    By default, shows all previously set wallpapers. Use options to limit
    or filter the list.
    """
    hm = HistoryManager()
    try:
        all_entries = hm.read()
    except Exception as e:
        err(ctx, "Failed to read history", e)

    if lines is not None:
        start_index = max(0, len(all_entries) - lines)
        entries = list(enumerate(all_entries))[start_index:]
    else:
        entries = list(enumerate(all_entries))

    if unique:
        seen = set()
        deduped = []
        for i, entry in entries:
            if entry.path not in seen:
                seen.add(entry.path)
                deduped.append((i, entry))
        entries = deduped

    for i, entry in entries:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry.time))
        log(f"{i+1:>3}: {entry.path} ({timestamp})", silent=ctx.obj.get("silent"))


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin
# pylint: disable=too-many-branches
@history_cmd.command("rm", short_help="Remove entries from wallpaper history")
@click.help_option("--help", "-h")
@click.option("-i", "--index", type=int, help="Remove a single entry by index (1-based)")
@click.option("-A", "--all", is_flag=True, help="Remove all history entries")
@click.option("-D", "--duplicates", is_flag=True, help="Remove duplicate entries")
@click.option(
    "-S",
    "--since",
    type=click.DateTime(formats=["%Y-%m-%d", "%Y-%m-%d %H:%M"]),
    help="Only keep entries after this date",
)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def history_rm_cmd(ctx, index, all, duplicates, since, yes):
    """
    Remove specific, duplicate, or old entries from wallpaper history.

    Dates must be in the format: YYYY-MM-DD or YYYY-MM-DD HH:MM
    """
    hm = HistoryManager()
    try:
        entries = hm.read()
    except Exception as e:
        err(ctx, "Failed to read history", e)

    original_count = len(entries)

    if not entries:
        log("No history to modify.", silent=ctx.obj.get("silent"))
        return

    if index is not None:
        if index < 1 or index > original_count:
            log(f"Invalid index: {index}. Must be between 1 and {original_count}.", silent=False)
            return

        entry = entries[index - 1]
        if not yes:
            click.confirm(f"Remove entry {index}: {entry.path}?", abort=True)

        try:
            hm.remove_by_index(index - 1)
        except Exception as e:
            err(ctx, f"Failed to remove history entry {index}", e)

        log(f"Removed entry {index}: {entry.path}", silent=ctx.obj.get("silent"))
        return

    remaining = entries[:]

    if since:
        cutoff = int(since.timestamp())
        remaining = [e for e in remaining if e.time >= cutoff]

    if duplicates:
        seen = {}
        for entry in reversed(remaining):
            seen[entry.path] = entry
        remaining = list(reversed(list(seen.values())))

    if all and not since and not duplicates:
        if not yes:
            click.confirm("Remove all history entries?", abort=True)
        try:
            hm.remove_all()
        except Exception as e:
            err(ctx, "Failed to remove all history entries", e)
        log("All history cleared.", silent=ctx.obj.get("silent"))
        return

    if len(remaining) == original_count:
        log("No entries removed.", silent=ctx.obj.get("silent"))
        return

    if not yes:
        removed = original_count - len(remaining)
        log(f"{original_count} entries found. {removed} will be removed.", silent=False)
        click.confirm("Proceed with removal?", abort=True)
