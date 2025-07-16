#!/usr/bin/env python

import logging
import os
import socket

from sw_lib.config import Config, ConfigError, ConfigLoadError, ConfigValidationError


class SocketServer:
    def __init__(self, wallpaper_setter):
        try:
            self.config = Config()
            self.socket_path = str(self.config.socket_path)
        except ConfigLoadError as e:
            raise RuntimeError("Failed to load configuration") from e
        except ConfigValidationError as e:
            raise RuntimeError("Invalid configuration") from e
        except ConfigError as e:
            raise RuntimeError("Configuration error") from e

        self.wallpaper_setter = wallpaper_setter

        self.logger = logging.getLogger("sw-daemon.SocketServer")

        # Remove stale socket if exists
        try:
            os.unlink(self.socket_path)
        except FileNotFoundError:
            pass
        except Exception as e:
            self.logger.warning("Could not remove old socket file: %s", e)

        self.server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_sock.bind(self.socket_path)
        self.server_sock.listen(1)
        self.logger.info("SocketServer listening on %s", self.socket_path)

    def serve_forever(self):
        try:
            while True:
                client_sock, _ = self.server_sock.accept()
                with client_sock:
                    self.handle_client(client_sock)
        except KeyboardInterrupt:
            self.logger.info("Shutting down socket server...")
        finally:
            self.cleanup()

    def handle_client(self, client_sock):
        data = self.receive_data(client_sock)
        if not data:
            return

        if data.lower().startswith("set "):
            image_path = data[4:].strip()
            self.handle_set_command(client_sock, image_path)
        else:
            self.send_error(client_sock, "Unknown command")

    def receive_data(self, client_sock):
        try:
            data = client_sock.recv(1024).decode().strip()
            self.logger.info("Received: %s", data)
            return data
        except Exception as e:
            self.logger.error("Error reading from client: %s", e)
            return None

    def handle_set_command(self, client_sock, image_path):
        self.logger.info("Setting wallpaper to: %s", image_path)
        try:
            self.wallpaper_setter.set_image(image_path)
            client_sock.sendall(b"OK\n")
        except Exception as e:
            self.logger.error("Error setting wallpaper: %s", e)
            self.send_error(client_sock, str(e))

    def send_error(self, client_sock, message):
        try:
            client_sock.sendall(f"ERROR: {message}\n".encode())
        except Exception as e:
            self.logger.error("Error sending error message to client: %s", e)

    def cleanup(self):
        self.server_sock.close()
        try:
            os.unlink(self.socket_path)
        except Exception:
            pass
