"""
Single instance manager using localhost loopback socket.
Ensures only one instance of Animated Cursor Buddy runs at a time.
When a second instance is launched (e.g. from Desktop shortcut),
it signals the running instance to bring its Settings dialog to the front.
"""

import socket
import threading
from typing import Callable

DEFAULT_PORT = 58293


class SingleInstanceManager:
    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.server_socket: socket.socket | None = None
        self._running = False

    def check_or_register(self, on_wake_signal: Callable[[], None]) -> bool:
        """
        Returns True if this is the first/primary instance.
        Returns False if another instance was already running and has been notified.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("127.0.0.1", self.port))
            sock.listen(5)
            self.server_socket = sock
            self._running = True

            # Start listener thread for subsequent launches
            t = threading.Thread(target=self._listen_loop, args=(on_wake_signal,), daemon=True)
            t.start()
            return True
        except OSError:
            # Port is occupied by another instance
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.settimeout(2.0)
                client.connect(("127.0.0.1", self.port))
                client.sendall(b"SHOW\n")
                client.close()
                print("[Instance] Signaled running instance to focus settings window.")
            except Exception as e:
                print(f"[Instance] Could not signal running instance: {e}")
            return False

    def _listen_loop(self, callback: Callable[[], None]):
        while self._running and self.server_socket:
            try:
                conn, _ = self.server_socket.accept()
                with conn:
                    msg = conn.recv(64)
                    if b"SHOW" in msg and callback:
                        callback()
            except Exception:
                break

    def stop(self):
        self._running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None
