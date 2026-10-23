"""
Comprehensive System Cursor Manager for Windows.
Hides ALL native cursor variants (arrow, hand pointer, I-beam, resize, busy, etc.)
while keeping physical mouse movement and interactive hover states fully active.
Restores all standard Windows cursors instantly upon return of user input or application exit.
"""

import atexit
import ctypes
import win32con

# Complete list of standard Windows system cursor resource IDs (OCR)
OCR_CURSOR_IDS = [
    32512,  # OCR_NORMAL (Standard arrow)
    32513,  # OCR_IBEAM (Text selection / insertion)
    32514,  # OCR_WAIT (Hourglass / busy)
    32515,  # OCR_CROSS (Crosshair)
    32516,  # OCR_UP (Vertical arrow)
    32641,  # OCR_ICON
    32642,  # OCR_SIZENWSE (Diagonal resize 1)
    32643,  # OCR_SIZENESW (Diagonal resize 2)
    32644,  # OCR_SIZEWE (Horizontal resize)
    32645,  # OCR_SIZENS (Vertical resize)
    32646,  # OCR_SIZEALL (Move / 4-way arrow)
    32648,  # OCR_NO (Slashed circle / prohibited)
    32649,  # OCR_HAND (Pointing hand over links/buttons)
    32650,  # OCR_APPSTARTING (Arrow with small hourglass)
    32651,  # OCR_HELP (Arrow with question mark)
    32671,  # OCR_PIN (Location pin)
    32672,  # OCR_PERSON (Person cursor)
]


class CursorHider:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.is_hidden = False

        # Fail-safe hooks to guarantee cursor restoration under all conditions
        atexit.register(self.restore)
        self._setup_ctrl_handler()

    def _setup_ctrl_handler(self):
        try:
            handler_proto = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)

            def _handler(ctrl_type):
                self.restore()
                return False

            self._ctrl_handler_ref = handler_proto(_handler)
            self.kernel32.SetConsoleCtrlHandler(self._ctrl_handler_ref, True)
        except Exception:
            pass

    def _create_blank_cursor(self):
        """Creates a 1x1 100% transparent cursor handle."""
        and_mask = (ctypes.c_ubyte * 4)(0xFF, 0xFF, 0xFF, 0xFF)
        xor_mask = (ctypes.c_ubyte * 4)(0x00, 0x00, 0x00, 0x00)
        return self.user32.CreateCursor(None, 0, 0, 1, 1, and_mask, xor_mask)

    def hide(self):
        """
        Replaces every system cursor variant with a transparent cursor.
        Physical mouse events (WM_MOUSEMOVE, hover effects, CSS styles) continue
        to trigger perfectly on underlying applications, but no native cursor is rendered.
        """
        if self.is_hidden:
            return

        try:
            for cid in OCR_CURSOR_IDS:
                h_blank = self._create_blank_cursor()
                if h_blank:
                    # SetSystemCursor replaces the cursor and takes ownership of h_blank
                    if not self.user32.SetSystemCursor(h_blank, cid):
                        self.user32.DestroyCursor(h_blank)

            self.is_hidden = True
        except Exception as e:
            print(f"[CursorHider] Error hiding system cursors: {e}")

    def restore(self):
        """
        Instantly restores all standard Windows system cursors to system defaults
        using official SPI_SETCURSORS API.
        """
        if self.is_hidden:
            try:
                self.user32.SystemParametersInfoW(win32con.SPI_SETCURSORS, 0, None, 0)
            except Exception as e:
                print(f"[CursorHider] Error restoring system cursors: {e}")
            finally:
                self.is_hidden = False
