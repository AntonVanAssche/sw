#!/usr/bin/env python

import socket

from sw_lib.config import Config, ConfigError


class SWDaemonError(Exception):
    """Base exception for SWDaemon-related errors."""


class SWDaemonConnectionError(SWDaemonError):
    """Raised when the client cannot connect to the daemon."""


class SWDaemonTimeoutError(SWDaemonConnectionError):
    """Raised when the connection to the daemon times out."""


class SWDaemonProtocolError(SWDaemonError):
    """Raised when there is an error in the communication protocol or response."""


class SWDaemonClient:
    def __init__(self, timeout=5):
        try:
            self.socket_path = str(Config().socket_path)
        except ConfigError as e:
            raise RuntimeError("Failed to load socket path from config") from e

        self.timeout = timeout

    def _send_command(self, command: str) -> str:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(self.timeout)
                client.connect(self.socket_path)
                client.sendall((command + "\n").encode())

                data = b""
                while True:
                    chunk = client.recv(4096)
                    if not chunk:
                        break
                    data += chunk

                response = data.decode(errors="replace").strip()
                if not response:
                    raise SWDaemonProtocolError("No response received from daemon.")

                return response

        except socket.timeout as e:
            raise SWDaemonTimeoutError(
                f"Connection to daemon at {self.socket_path} timed out after {self.timeout}s."
            ) from e
        except (ConnectionRefusedError, FileNotFoundError) as e:
            raise SWDaemonConnectionError(
                f"Failed to connect to daemon at {self.socket_path}. Is the daemon running?"
            ) from e
        except socket.error as e:
            raise SWDaemonError(f"Socket error occurred during communication: {e}") from e
        except Exception as e:
            raise SWDaemonError(f"Unexpected error communicating with daemon: {e}") from e

    def set_wallpaper(self, image_path: str) -> str:
        response = self._send_command(f"SET {image_path}")
        if not response.startswith("OK"):
            raise SWDaemonProtocolError(f"Daemon returned error: {response}")
        return response
