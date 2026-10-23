"""
System Tray controller for Animated Cursor Buddy.
Runs quietly in the Windows notification area with control menus.
"""

from typing import Callable
from PIL import Image, ImageDraw
import pystray


def create_tray_icon_image(is_active: bool = False, is_paused: bool = False) -> Image.Image:
    """Generate a high-res crisp tray icon."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Base circle
    bg_color = "#363A4F"
    if is_paused:
        bg_color = "#ED8796"
    elif is_active:
        bg_color = "#A6DA95"

    d.ellipse((4, 4, 60, 60), fill=bg_color, outline="#CAD3F5", width=3)

    # Stylized mouse arrow inside
    arrow_pts = [
        (22, 16),
        (22, 44),
        (31, 36),
        (42, 46),
        (46, 42),
        (35, 32),
        (44, 32),
    ]
    d.polygon(arrow_pts, fill="#FFFFFF", outline="#181926")

    # Sparkling dot
    sparkle_color = "#FFD700" if is_active else "#8AADF4"
    d.ellipse((44, 12, 54, 22), fill=sparkle_color)

    return img


class SystemTrayManager:
    def __init__(
        self,
        on_open_settings: Callable[[], None],
        on_toggle_pause: Callable[[], None],
        on_test_now: Callable[[], None],
        on_quit: Callable[[], None],
    ):
        self.on_open_settings = on_open_settings
        self.on_toggle_pause = on_toggle_pause
        self.on_test_now = on_test_now
        self.on_quit = on_quit

        self.is_paused = False
        self.is_buddy_active = False

        self.icon = pystray.Icon(
            "CursorBuddy",
            icon=create_tray_icon_image(),
            title="Animated Cursor Buddy",
            menu=self._create_menu(),
        )

    def _create_menu(self):
        status_text = "⏸ Paused" if self.is_paused else ("✨ Active (Wandering)" if self.is_buddy_active else "👀 Watching for Idle")
        pause_label = "▶ Resume Buddy" if self.is_paused else "⏸ Pause Buddy"

        return pystray.Menu(
            pystray.MenuItem(f"Cursor Buddy ({status_text})", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🚀 Summon Buddy Now", lambda: self.on_test_now()),
            pystray.MenuItem(pause_label, lambda: self.on_toggle_pause()),
            pystray.MenuItem("⚙ Settings...", lambda: self.on_open_settings()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Exit", lambda: self.on_quit()),
        )

    def update_state(self, is_active: bool, is_paused: bool):
        changed = (self.is_buddy_active != is_active) or (self.is_paused != is_paused)
        if changed:
            self.is_buddy_active = is_active
            self.is_paused = is_paused
            self.icon.icon = create_tray_icon_image(is_active=is_active, is_paused=is_paused)
            self.icon.menu = self._create_menu()

    def start(self):
        self.icon.run_detached()

    def stop(self):
        self.icon.stop()
