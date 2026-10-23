"""
Power manager for Windows to prevent sleep or display turn-off while buddy is active.
Uses the Win32 SetThreadExecutionState API.
"""

import ctypes

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002
ES_AWAYMODE_REQUIRED = 0x00000040


class PowerManager:
    def __init__(self):
        self._kernel32 = ctypes.windll.kernel32
        self._is_preventing_sleep = False

    def prevent_sleep(self, keep_display_on: bool = True):
        """Keeps the system and display awake while active."""
        flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED
        if keep_display_on:
            flags |= ES_DISPLAY_REQUIRED
        self._kernel32.SetThreadExecutionState(flags)
        self._is_preventing_sleep = True

    def restore_sleep(self):
        """Restores normal Windows power-saving and sleep behavior."""
        if self._is_preventing_sleep:
            self._kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            self._is_preventing_sleep = False

    @property
    def is_active(self) -> bool:
        return self._is_preventing_sleep
