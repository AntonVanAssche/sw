# cmds/__init__.py

from .config import config_cmd
from .history import history_cmd
from .next import next_cmd
from .prev import prev_cmd
from .queue import queue_cmd
from .set import set_cmd
from .status import status_cmd
from .timer import timer_cmd

__doc__ = """
cmds - Module for handling commands related to wallpaper management.

Commands available:
- config_cmd: Command for managing the configuration.
- status_cmd: Command for getting the current wallpaper.
- next_cmd: Command for setting the next wallpaper.
- prev_cmd: Command for setting the previous wallpaper.
- queue_cmd: Command for managing the wallpaper queue.
- set_cmd: Command for setting a specific wallpaper.
- timer_cmd: Command for managing wallpaper timer settings.
"""

__all__ = [
    "config_cmd",
    "status_cmd",
    "history_cmd",
    "next_cmd",
    "prev_cmd",
    "queue_cmd",
    "set_cmd",
    "timer_cmd",
]
