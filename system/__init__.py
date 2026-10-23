from .audio import SoundManager
from .autostart import is_autostart_enabled, set_autostart
from .cursor_hider import CursorHider
from .hotkey import GlobalHotkeyListener
from .idle_detector import IdleDetector
from .media_detector import MediaDetector
from .power_manager import PowerManager
from .screen import get_desktop_work_area
from .single_instance import SingleInstanceManager

__all__ = [
    "IdleDetector",
    "PowerManager",
    "SoundManager",
    "CursorHider",
    "MediaDetector",
    "is_autostart_enabled",
    "set_autostart",
    "GlobalHotkeyListener",
    "SingleInstanceManager",
    "get_desktop_work_area",
]
