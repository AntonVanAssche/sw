#!/usr/bin/env python3

from .config import Config
from .history import HistoryManager
from .queue import QueueManager
from .timer import TimerManager
from .wallpaper import WallpaperManager

__doc__ = """
sw.core - Core module for managing configuration, queues, and wallpapers.

Managers available:
- Config: Handles the configuration of the application.
- QueueManager: Manages the queue of wallpapers.
- TimerManager: Manages the systemd timer for wallpaper changes.
- WallpaperManager: Handles the wallpaper-related operations.
"""

__all__ = ["Config", "HistoryManager", "QueueManager", "TimerManager", "WallpaperManager"]
