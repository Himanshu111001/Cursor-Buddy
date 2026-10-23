"""
Animated Cursor Buddy 🖱️✨
Main Application Entry Point & Lifecycle Coordinator.
"""

import argparse
import math
import sys
import time
import tkinter as tk
import win32api
import win32con

# Configure safe utf-8 stdout/stderr on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from characters import get_character
from config import BuddyConfig
from engine import MovementEngine, OverlayWindow, ParticleSystem
from system import (
    CursorHider,
    GlobalHotkeyListener,
    IdleDetector,
    PowerManager,
    SingleInstanceManager,
    SoundManager,
    get_desktop_work_area,
)
from ui import SettingsDialog, SystemTrayManager


class CursorBuddyApp:
    def __init__(self, initial_test_mode: bool = False, open_settings_on_start: bool = False):
        # Single-instance check
        self.single_instance = SingleInstanceManager()
        if not self.single_instance.check_or_register(on_wake_signal=self._open_settings_threadsafe):
            # Another instance is already running and was signaled to focus.
            sys.exit(0)

        self.config = BuddyConfig.load()
        self.is_active = False
        self.is_paused = False
        self.force_wake = initial_test_mode

        # System services
        self.idle_detector = IdleDetector()
        self.power_manager = PowerManager()
        self.cursor_hider = CursorHider()
        self.particles = ParticleSystem()
        self.sound = SoundManager(enabled=self.config.sound_enabled)

        # Global Hotkey (Ctrl + Alt + B)
        self.hotkey = GlobalHotkeyListener(on_hotkey=self._on_hotkey_threadsafe)
        self.hotkey.start()

        # Desktop work area bounds (excluding Windows taskbar)
        work_bounds = get_desktop_work_area()

        # AI Movement Engine confined strictly inside screen work area
        self.movement = MovementEngine(bounds=work_bounds)
        self.movement.set_speed_profile(self.config.movement_speed)

        # Tkinter Root & Overlay Window
        self.root = tk.Tk()
        self.root.withdraw()  # Root stays permanently hidden as coordinator
        self.active_character = get_character(self.config.character)
        self.overlay = OverlayWindow(
            parent=self.root,
            config=self.config,
            character=self.active_character,
            particles=self.particles,
        )

        # Settings Dialog
        self.settings_dialog = SettingsDialog(
            parent=self.root,
            config=self.config,
            on_save_callback=self._on_settings_saved,
            on_test_callback=self._on_summon_buddy,
        )

        # System Tray Integration
        self.tray = SystemTrayManager(
            on_open_settings=self._open_settings_threadsafe,
            on_toggle_pause=self._toggle_pause_threadsafe,
            on_test_now=self._summon_buddy_threadsafe,
            on_quit=self._quit_threadsafe,
        )

        # Tracking state
        self.last_tick_time = time.time()
        self.activate_time = 0.0
        self.expected_cursor_x = 0
        self.expected_cursor_y = 0

        # Start background tray
        self.tray.start()

        if open_settings_on_start:
            self.root.after(200, self.settings_dialog.show)

        # Kick off 60 FPS update loop
        self.root.after(16, self._tick)

    def _on_settings_saved(self, new_config: BuddyConfig):
        self.config = new_config
        self.active_character = get_character(self.config.character)
        self.overlay.set_character(self.active_character)
        self.movement.set_speed_profile(self.config.movement_speed)
        self.sound.enabled = self.config.sound_enabled
        if self.is_active:
            if self.config.hide_default_cursor and self.config.move_physical_cursor:
                self.cursor_hider.hide()
            else:
                self.cursor_hider.restore()
        print(f"[Buddy] Updated settings: character={self.config.character}, timeout={self.config.idle_timeout_seconds}s")

    def _on_hotkey_threadsafe(self):
        self.root.after(0, self._on_hotkey_toggle)

    def _on_hotkey_toggle(self):
        """Hotkey Ctrl+Alt+B pressed: toggle wake/dismiss."""
        if self.is_active:
            self._deactivate_buddy()
        else:
            self._on_summon_buddy()

    def _open_settings_threadsafe(self):
        self.root.after(0, self.settings_dialog.show)

    def _toggle_pause_threadsafe(self):
        self.root.after(0, self._toggle_pause)

    def _summon_buddy_threadsafe(self):
        self.root.after(0, self._on_summon_buddy)

    def _quit_threadsafe(self):
        self.root.after(0, self.shutdown)

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused and self.is_active:
            self._deactivate_buddy()
        self.tray.update_state(is_active=self.is_active, is_paused=self.is_paused)
        print(f"[Buddy] Paused: {self.is_paused}")

    def _on_summon_buddy(self):
        self.force_wake = True
        self.is_paused = False
        print("[Buddy] Manual summon triggered!")

    def _activate_buddy(self):
        """Wakes the animated companion and begins autonomous roaming."""
        bounds = get_desktop_work_area()
        self.movement.set_bounds(bounds)

        cur_x, cur_y = self.idle_detector.get_cursor_position()
        self.movement.reset_to_position(cur_x, cur_y)
        self.expected_cursor_x = int(self.movement.x)
        self.expected_cursor_y = int(self.movement.y)

        # Synchronize timers so first frame dt is clean
        current_time = time.time()
        self.last_tick_time = current_time
        self.activate_time = current_time

        if self.config.keep_screen_awake:
            self.power_manager.prevent_sleep(keep_display_on=True)

        if self.config.hide_default_cursor and self.config.move_physical_cursor:
            self.cursor_hider.hide()

        # Position and pre-render overlay window BEFORE making it visible
        self.overlay.show(
            initial_x=self.movement.x,
            initial_y=self.movement.y,
            state=self.movement.state,
            facing_right=self.movement.facing_right,
        )

        self.is_active = True
        self.force_wake = False
        self.tray.update_state(is_active=True, is_paused=self.is_paused)
        self.sound.play_wake()
        print(f"[Buddy] ✨ Activated smoothly at cursor position ({int(self.movement.x)}, {int(self.movement.y)})")

    def _deactivate_buddy(self):
        """Instantly restores normal mouse control and hides the companion."""
        self.cursor_hider.restore()
        self.overlay.hide()
        self.power_manager.restore_sleep()
        self.is_active = False
        self.force_wake = False
        self.tray.update_state(is_active=False, is_paused=self.is_paused)
        self.sound.play_sleep()
        print("[Buddy] 👋 User returned! Restoring standard cursor control.")

    def _tick(self):
        current_time = time.time()
        dt = min(0.05, current_time - self.last_tick_time)
        self.last_tick_time = current_time

        if not self.is_paused:
            idle_seconds = self.idle_detector.get_idle_seconds()

            if not self.is_active:
                # Check if system has been idle long enough or forced summon
                if self.force_wake or idle_seconds >= self.config.idle_timeout_seconds:
                    self._activate_buddy()
            else:
                # Active mode: Check if user physically touched mouse or keyboard
                user_returned = False

                # Grace period: ignore input within first 600ms of activation to prevent premature dismissal
                if (current_time - self.activate_time) > 0.6:
                    # 1. Hardware input event within last 250ms
                    if self.idle_detector.is_user_active(threshold_ms=250):
                        user_returned = True

                    # 2. Physical mouse moved away from where companion placed it
                    if self.config.move_physical_cursor:
                        real_x, real_y = self.idle_detector.get_cursor_position()
                        deviation = math.hypot(real_x - self.expected_cursor_x, real_y - self.expected_cursor_y)
                        if deviation > 20:  # Physical nudge detected
                            user_returned = True

                if user_returned and not self.force_wake:
                    self._deactivate_buddy()
                else:
                    # Update buddy movement and render frame
                    bx, by, state = self.movement.update(dt)

                    # Move physical Windows cursor if enabled
                    if self.config.move_physical_cursor:
                        self.idle_detector.set_cursor_position(bx, by)
                        self.expected_cursor_x = int(bx)
                        self.expected_cursor_y = int(by)

                    # Render animation frame
                    self.overlay.render(
                        x=bx,
                        y=by,
                        state=state,
                        facing_right=self.movement.facing_right,
                        time_sec=current_time,
                    )

        # Schedule next animation frame (~60 FPS)
        self.root.after(16, self._tick)

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        print("[Buddy] Shutting down...")
        self.cursor_hider.restore()
        self.single_instance.stop()
        self.hotkey.stop()
        self._deactivate_buddy()
        self.tray.stop()
        self.root.destroy()
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Animated Cursor Buddy")
    parser.add_argument("--test", action="store_true", help="Start buddy immediately without waiting for idle")
    parser.add_argument("--settings", action="store_true", help="Open the settings window on launch")
    parser.add_argument("--silent", action="store_true", help="Start silently in background tray without opening settings")
    args, _ = parser.parse_known_args()

    # Open settings on launch by default unless --silent or --test is given
    open_settings = args.settings or (not args.silent and not args.test)

    app = CursorBuddyApp(initial_test_mode=args.test, open_settings_on_start=open_settings)
    app.run()


if __name__ == "__main__":
    main()
