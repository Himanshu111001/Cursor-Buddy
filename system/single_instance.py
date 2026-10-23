"""
Single instance manager using Windows Named Mutex and inter-process socket signaling.
Guarantees strictly ONE instance of Animated Cursor Buddy runs at any time.
"""

import ctypes
import socket
import sys
import threading
from typing import Callable

MUTEX_NAME = "Local\\AnimatedCursorBuddy_Instance_Mutex_v2"
DEFAULT_PORT = 58293
ERROR_ALREADY_EXISTS = 183


class SingleInstanceManager:
    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.mutex = None
        self.server_socket: socket.socket | None = None
        self._running = False
        self.kernel32 = ctypes.windll.kernel32

    def check_or_register(self, on_wake_signal: Callable[[], None]) -> bool:
        """
        Returns True if this is the only running instance.
        Returns False if another instance is already running (signals it to bring Settings to front).
        """
        # 1. Atomic Windows Named Mutex check
        self.mutex = self.kernel32.CreateMutexW(None, False, MUTEX_NAME)
        last_error = self.kernel32.GetLastError()

        if last_error == ERROR_ALREADY_EXISTS:
            # Another instance is DEFINITELY running!
            self._signal_existing_instance()
            if self.mutex:
                try:
                    self.kernel32.CloseHandle(self.mutex)
                except Exception:
                    pass
                self.mutex = None
            return False

        # 2. We are the unique primary instance; open listening socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # NEVER use SO_REUSEADDR on Windows; it allows multiple processes to bind same port
            sock.bind(("127.0.0.1", self.port))
            sock.listen(5)
            self.server_socket = sock
            self._running = True

            t = threading.Thread(target=self._listen_loop, args=(on_wake_signal,), daemon=True)
            t.start()
            return True
        except Exception as e:
            print(f"[Instance] Warning binding single instance socket: {e}")
            return True

    def _signal_existing_instance(self):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1.5)
            client.connect(("127.0.0.1", self.port))
            client.sendall(b"SHOW\n")
            client.close()
            print("[Instance] Signaled running instance to focus settings window.")
        except Exception as e:
            print(f"[Instance] Could not send signal to running instance: {e}")

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
        if self.mutex:
            try:
                self.kernel32.CloseHandle(self.mutex)
            except Exception:
                pass
            self.mutex = None
