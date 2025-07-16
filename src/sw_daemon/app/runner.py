#!/usr/bin/env python

import logging
import threading

from sw_daemon.ipc.socket import SocketServer
from sw_lib.config import Config, ConfigError, ConfigLoadError, ConfigValidationError
from sw_lib.history import HistoryEntryNotFoundError, HistoryManager

from .core import SWDaemon

logger = logging.getLogger("sw-daemon.runner")


def start(image_path=None):
    try:
        config = Config()
        hm = HistoryManager(
            config.history_file,
            config.history_limit,
            config.recency_timeout,
        )

        if image_path is None:
            if not hm.is_empty():
                image_path = hm.get(-1).path

        setter = SWDaemon(image_path)
        setter.assert_initialised()

        server = SocketServer(setter)
        socket_thread = threading.Thread(target=server.serve_forever, daemon=True)
        socket_thread.start()

        try:
            setter.run()
        except KeyboardInterrupt:
            logger.warning("Exiting on keyboard interrupt...")
            setter.running = False
    except (ConfigLoadError, ConfigValidationError, ConfigError) as e:
        logger.error("Failed to load configuration: %s", e)
    except (HistoryEntryNotFoundError, ValueError, IndexError) as e:
        logger.error("Error resolving wallpaper path from history: %e", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)
