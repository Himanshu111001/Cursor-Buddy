"""
Idle and user activity detector for Windows using Win32 API.
Detects when the user has stepped away and instantly detects when they return.
"""

import ctypes
import ctypes.wintypes


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint),
    ]


class IdleDetector:
    def __init__(self):
        self._last_input_info = LASTINPUTINFO()
        self._last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        self._user32 = ctypes.windll.user32
        self._kernel32 = ctypes.windll.kernel32

    def get_last_input_tick(self) -> int:
        """Returns the raw Windows tick count when the last hardware input occurred."""
        if self._user32.GetLastInputInfo(ctypes.byref(self._last_input_info)):
            return self._last_input_info.dwTime
        return 0

    def get_idle_ms(self) -> int:
        """Returns the number of milliseconds since the last hardware user input (keyboard, mouse, touch)."""
        if self._user32.GetLastInputInfo(ctypes.byref(self._last_input_info)):
            current_tick = self._kernel32.GetTickCount()
            # Handle 49.7 day tick count rollover
            idle_ms = (current_tick - self._last_input_info.dwTime) & 0xFFFFFFFF
            return idle_ms
        return 0

    def get_idle_seconds(self) -> float:
        """Returns the number of seconds since the last hardware user input."""
        return self.get_idle_ms() / 1000.0

    def is_user_active(self, threshold_ms: int = 300) -> bool:
        """Returns True if user hardware input occurred within the last threshold_ms milliseconds."""
        return self.get_idle_ms() < threshold_ms

    def get_cursor_position(self) -> tuple[int, int]:
        """Returns the current screen cursor position (x, y)."""
        pt = ctypes.wintypes.POINT()
        self._user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    def set_cursor_position(self, x: int, y: int):
        """Sets the cursor position programmatically."""
        self._user32.SetCursorPos(int(x), int(y))
