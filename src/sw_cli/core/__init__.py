#!/usr/bin/env python3

from .history import HistoryManager
from .queue import QueueManager
from .timer import TimerManager
from .wallpaper import WallpaperManager

__doc__ = """
sw_cli.core - Core module for managing configuration, queues, and wallpapers.

Managers available:
- QueueManager: Manages the queue of wallpapers.
- TimerManager: Manages the systemd timer for wallpaper changes.
- WallpaperManager: Handles the wallpaper-related operations.
"""

__all__ = ["HistoryManager", "QueueManager", "TimerManager", "WallpaperManager"]
