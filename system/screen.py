"""
Display metrics and DPI awareness manager for Windows.
Retrieves exact desktop work area (excluding taskbar) and coordinates.
"""

import ctypes
import ctypes.wintypes
import win32con

# Enable High-DPI awareness so coordinates match physical pixels perfectly
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def get_desktop_work_area() -> tuple[int, int, int, int]:
    """
    Returns (left, top, right, bottom) of the primary desktop work area,
    strictly excluding the Windows taskbar and docked toolbars.
    """
    rect = ctypes.wintypes.RECT()
    success = ctypes.windll.user32.SystemParametersInfoW(
        win32con.SPI_GETWORKAREA, 0, ctypes.byref(rect), 0
    )
    if success and rect.right > rect.left and rect.bottom > rect.top:
        return rect.left, rect.top, rect.right, rect.bottom
    # Fallback to standard primary screen metrics
    w = ctypes.windll.user32.GetSystemMetrics(win32con.SM_CXSCREEN)
    h = ctypes.windll.user32.GetSystemMetrics(win32con.SM_CYSCREEN)
    return 0, 0, w, max(400, h - 48)
