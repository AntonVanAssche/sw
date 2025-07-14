#!/usr/bin/env python

import logging
import threading

from sw_daemon.ipc.socket import SocketServer

from .core import SWDaemon

logger = logging.getLogger("sw-daemon.runner")


def start(image_path=None):
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
