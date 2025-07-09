import logging
import os
import socket

SOCKET_PATH = "/tmp/sw-daemon.sock"


class SocketServer:
    def __init__(self, socket_path, wallpaper_setter):
        self.socket_path = socket_path
        self.wallpaper_setter = wallpaper_setter

        self.logger = logging.getLogger("sw-daemon.SocketServer")

        # Remove stale socket if exists
        try:
            os.unlink(self.socket_path)
        except FileNotFoundError:
            pass
        except Exception as e:
            self.logger.warning(f"Could not remove old socket file: {e}")

        self.server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_sock.bind(self.socket_path)
        self.server_sock.listen(1)
        self.logger.info(f"SocketServer listening on {self.socket_path}")

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
            self.logger.info(f"Received: {data}")
            return data
        except Exception as e:
            self.logger.error(f"Error reading from client: {e}")
            return None

    def handle_set_command(self, client_sock, image_path):
        self.logger.info(f"Setting wallpaper to: {image_path}")
        try:
            self.wallpaper_setter.set_image(image_path)
            client_sock.sendall(b"OK\n")
        except Exception as e:
            self.logger.error(f"Error setting wallpaper: {e}")
            self.send_error(client_sock, str(e))

    def send_error(self, client_sock, message):
        try:
            client_sock.sendall(f"ERROR: {message}\n".encode())
        except Exception as e:
            self.logger.error(f"Error sending error message to client: {e}")

    def cleanup(self):
        self.server_sock.close()
        try:
            os.unlink(self.socket_path)
        except Exception:
            pass
