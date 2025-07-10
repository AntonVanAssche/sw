#!/usr/bin/env python

import time

import click

from sw_cli.core.history import HistoryManager
from sw_cli.utils.common import err, log, warn
from sw_cli.utils.style import bold, green, red, yellow


# pylint: disable=unused-argument
@click.group("history", short_help="Manage wallpaper history")
@click.help_option("--help", "-h")
@click.pass_context
def history_cmd(ctx):
    """
    Manage the wallpaper history.

    Provides utilities to list and remove previously set wallpapers.
    """


# pylint: disable=too-many-locals
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
        err("Failed to read history", e, ctx)

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
        idx_str = yellow(f"{i+1:>3}")
        path_str = green(entry.path)
        time_str = yellow(f"({timestamp})")
        log(f"{idx_str}: {path_str} {time_str}", ctx)


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin
# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
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
        err("Failed to read history", e, ctx)

    original_count = len(entries)

    if not entries:
        log("No history to modify.", ctx)
        return

    if index is not None:
        if index < 1 or index > original_count:
            log(f"Invalid index: {index}. Must be between 1 and {original_count}.", ctx)
            return

        entry = entries[index - 1]
        if not yes:
            click.confirm(f"Remove entry {index}: {entry.path}?", abort=True)

        try:
            hm.remove_by_index(index - 1)
        except Exception as e:
            err(f"Failed to remove history entry {index}", e, ctx)

        log(f"Removed entry {green(entry.path)}", ctx)
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
            err("Failed to remove all history entries", e, ctx)
        log(green("All history cleared."), ctx)
        return

    if len(remaining) == original_count:
        warn("No entries removed.", ctx)
        return

    if not yes:
        removed = original_count - len(remaining)
        log(f"{green(original_count)} entries found. {red(removed)} will be removed.", ctx)
        click.confirm(bold(yellow("Proceed with removal?")), abort=True)

    remaining_set = set(remaining)
    removed_entries = []
    try:
        for i in reversed(range(original_count)):
            if i == original_count - 1:
                continue  # Never delete the last entry

            if entries[i] not in remaining_set:
                removed_entries.append(entries[i].path)
                hm.remove_by_index(i)
    except Exception as e:
        err("Failed to remove some history entries", e, ctx)
        return

    for path in removed_entries:
        log(f"Removed entry: {red(path)}", ctx)

    removed = len(removed_entries)
    log(f"Removed {red(removed)} entries from history.", ctx)
