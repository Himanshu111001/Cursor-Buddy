"""
Global hotkey listener for Windows.
Listens for Ctrl + Alt + B system-wide to summon or dismiss the companion.
"""

import ctypes
import ctypes.wintypes
import threading
from typing import Callable

user32 = ctypes.windll.user32

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_NOREPEAT = 0x4000
VK_B = 0x42  # 'B' key
WM_HOTKEY = 0x0312
HOTKEY_ID = 4242


class GlobalHotkeyListener:
    def __init__(self, on_hotkey: Callable[[], None]):
        self.on_hotkey = on_hotkey
        self._thread: threading.Thread | None = None
        self._thread_id: int | None = None
        self._running = False

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        self._thread_id = threading.get_native_id()
        # Register Ctrl + Alt + B
        success = user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_B)
        if not success:
            print("[Hotkey] Could not register Ctrl+Alt+B (may already be in use)")
            return

        print("[Hotkey] Registered global shortcut: Ctrl + Alt + B")
        msg = ctypes.wintypes.MSG()
        try:
            while self._running:
                # Pump messages for this thread
                ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if ret <= 0:
                    break
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    if self.on_hotkey:
                        self.on_hotkey()
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, HOTKEY_ID)

    def stop(self):
        self._running = False
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, 0x0012, 0, 0)  # WM_QUIT
