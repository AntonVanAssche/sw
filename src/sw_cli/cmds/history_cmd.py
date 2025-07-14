#!/usr/bin/env python

import time

import click

from sw_cli.history import (
    HistoryEntryNotFoundError,
    HistoryError,
    HistoryManager,
    HistoryNotFoundError,
    HistoryNotReadableError,
    HistoryParseError,
    HistoryWriteError,
)
from sw_cli.utils.common import err, log, warn
from sw_cli.utils.style import bold, green, red, yellow
from sw_lib.config import Config, ConfigError, ConfigLoadError, ConfigValidationError


def print_history_entries(ctx, entries):
    for i, entry in entries:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry.time))
        idx_str = yellow(f"{i + 1:>3}")
        path_str = green(entry.path)
        time_str = yellow(f"({timestamp})")
        log(f"{idx_str}: {path_str} {time_str}", ctx)


@click.group("history", short_help="Manage wallpaper history")
@click.help_option("--help", "-h")
def history_cmd():
    """
    Manage the wallpaper history.

    Provides utilities to list and remove previously set wallpapers.
    """


@history_cmd.command("list", short_help="List wallpaper history entries")
@click.help_option("--help", "-h")
@click.option("-n", "--lines", type=int, help="Show only the last N entries")
@click.option("-u", "--unique", is_flag=True, help="Show only unique entries (remove duplicates)")
@click.pass_context
def history_list_cmd(ctx, lines, unique):
    """List entries in the wallpaper history."""
    try:
        config = Config()
        hm = HistoryManager(config.history_file, config.history_limit, config.recency_timeout)
        all_entries = hm.get()

        if lines:
            entries = list(enumerate(all_entries))[-lines:]
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

        print_history_entries(ctx, entries)

    except (ConfigLoadError, ConfigValidationError, ConfigError) as e:
        err("Configuration error.", e, ctx)
    except (HistoryNotFoundError, HistoryNotReadableError, HistoryParseError) as e:
        err(f"History file error: {e}", ctx)
    except HistoryError as e:
        err(f"Failed to read history: {e}", ctx)
    except Exception as e:
        err(f"Unexpected error: {e}", ctx)


def remove_by_index(ctx, hm, entries, index, yes):
    original_count = len(entries)
    if index < 1 or index > original_count:
        err(f"Invalid index: {index}. Must be between 1 and {original_count}.", ctx)
        return

    entry = hm.get(index - 1)
    if not yes:
        click.confirm(f"Remove entry {index}: {entry.path}?", abort=True)
    hm.remove_by_index(index - 1)
    log(f"Removed entry {red(entry.path)}", ctx)


def remove_all_entries(ctx, hm, yes):
    if not yes:
        click.confirm("Remove all history entries?", abort=True)
    hm.remove_all()
    log(green("All history cleared."), ctx)


def remove_filtered_entries(ctx, hm, entries, options):
    original_count = len(entries)
    remaining = entries[:]

    if options.get("since"):
        cutoff = int(options.get("since").timestamp())
        remaining = [e for e in remaining if e.time >= cutoff]

    if options.get("duplicates"):
        seen = {}
        for e in reversed(remaining):
            seen[e.path] = e
        remaining = list(reversed(list(seen.values())))

    if len(remaining) == original_count:
        warn("No entries removed.", ctx)
        return

    removed_count = original_count - len(remaining)
    if not options.get("yes"):
        log(f"{green(original_count)} entries found. {red(removed_count)} will be removed.", ctx)
        click.confirm(bold(yellow("Proceed with removal?")), abort=True)

    removed_entries = []
    # Never remove last entry
    for i in reversed(range(len(entries))):
        if i == len(entries) - 1:
            continue
        if entries[i] not in remaining:
            removed_entries.append(entries[i].path)
            hm.remove_by_index(i)

    for path in removed_entries:
        log(f"Removed entry: {red(path)}", ctx)

    log(f"Removed {red(len(removed_entries))} entries from history.", ctx)


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
@history_cmd.command("rm", short_help="Remove entries from wallpaper history")
@click.help_option("--help", "-h")
@click.option("-i", "--index", type=int, help="Remove a single entry by index (1-based)")
@click.option("-A", "--all-entries", "all_entries", is_flag=True, help="Remove all history entries")
@click.option("-D", "--duplicates", is_flag=True, help="Remove duplicate entries")
@click.option(
    "-S",
    "--since",
    type=click.DateTime(formats=["%Y-%m-%d", "%Y-%m-%d %H:%M"]),
    help="Only keep entries after this date",
)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def history_rm_cmd(ctx, index, all_entries, duplicates, since, yes):
    """Remove specific, duplicate, or old entries from wallpaper history."""
    try:
        config = Config()
        hm = HistoryManager(config.history_file, config.history_limit, config.recency_timeout)
        entries = hm.get()

        if not entries:
            log("No history to modify.", ctx)
            return

        if index is not None:
            remove_by_index(ctx, hm, entries, index, yes)
            return

        if all_entries and not since and not duplicates:
            remove_all_entries(ctx, hm, yes)
            return

        options = {
            "since": since,
            "duplicates": duplicates,
            "yes": yes,
        }
        remove_filtered_entries(ctx, hm, entries, options)

    except (ConfigLoadError, ConfigValidationError, ConfigError) as e:
        err("Configuration error.", e, ctx)
    except (HistoryNotFoundError, HistoryNotReadableError, HistoryParseError) as e:
        err(f"History file error: {e}", ctx)
    except HistoryEntryNotFoundError as e:
        err(f"Entry not found: {e}", ctx)
    except HistoryWriteError as e:
        err(f"Failed to write history: {e}", ctx)
    except HistoryError as e:
        err(f"History error: {e}", ctx)
    except click.Abort:
        log("Operation aborted by user.", ctx)
    except Exception as e:
        err(f"Unexpected error: {e}", ctx)
