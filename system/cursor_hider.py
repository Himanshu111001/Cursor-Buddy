"""
Manages hiding the default Windows mouse pointer while the animated companion is active,
and cleanly restoring standard cursors the instant user input is detected or on shutdown.
"""

import atexit
import ctypes
import win32con

OCR_NORMAL = 32512  # Standard arrow cursor


class CursorHider:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.is_hidden = False
        atexit.register(self.restore)

    def hide(self):
        """Hides the standard Windows arrow cursor by replacing it with a transparent cursor."""
        if self.is_hidden:
            return
        try:
            # Create a 1x1 100% transparent cursor
            and_mask = (ctypes.c_ubyte * 4)(0xFF, 0xFF, 0xFF, 0xFF)
            xor_mask = (ctypes.c_ubyte * 4)(0x00, 0x00, 0x00, 0x00)
            h_blank = self.user32.CreateCursor(None, 0, 0, 1, 1, and_mask, xor_mask)
            if h_blank:
                self.user32.SetSystemCursor(h_blank, OCR_NORMAL)
                self.is_hidden = True
        except Exception as e:
            print(f"[CursorHider] Could not hide cursor: {e}")

    def restore(self):
        """Instantly restores standard Windows system cursors."""
        if self.is_hidden:
            try:
                self.user32.SystemParametersInfoW(win32con.SPI_SETCURSORS, 0, None, 0)
            except Exception as e:
                print(f"[CursorHider] Could not restore cursor: {e}")
            finally:
                self.is_hidden = False
