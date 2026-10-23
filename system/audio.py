"""
Gentle procedural sound effects for Animated Cursor Buddy.
Runs asynchronously to avoid any impact on frame rate.
"""

import threading
import time
import winsound


class SoundManager:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def play_wake(self):
        """Rising two-tone wake chime."""
        if not self.enabled:
            return

        def _run():
            try:
                winsound.Beep(587, 70)  # D5
                time.sleep(0.03)
                winsound.Beep(880, 100)  # A5
            except Exception:
                pass

        threading.Thread(target=_run, daemon=True).start()

    def play_sleep(self):
        """Falling gentle dismiss chime."""
        if not self.enabled:
            return

        def _run():
            try:
                winsound.Beep(659, 70)  # E5
                time.sleep(0.03)
                winsound.Beep(440, 100)  # A4
            except Exception:
                pass

        threading.Thread(target=_run, daemon=True).start()

    def play_react(self):
        """Subtle chirp for playful reactions."""
        if not self.enabled:
            return

        def _run():
            try:
                winsound.Beep(784, 50)  # G5
            except Exception:
                pass

        threading.Thread(target=_run, daemon=True).start()
