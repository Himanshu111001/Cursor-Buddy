"""
Compact floating transparent sprite overlay window.
Eliminates reactivation jitter by updating coordinates and pre-rendering frame
before revealing the window on every idle activation.
"""

import math
import time
import tkinter as tk
import win32con
import win32gui
from characters.base_character import BaseCharacter
from config import BuddyConfig
from engine.particles import ParticleSystem


class OverlayWindow:
    CHROMA_KEY = "#010101"
    WINDOW_SIZE = 128  # 128x128 sprite box

    def __init__(self, parent: tk.Tk, config: BuddyConfig, character: BaseCharacter, particles: ParticleSystem):
        self.parent = parent
        self.config = config
        self.character = character
        self.particles = particles
        self.is_visible = False

        # Dedicated Toplevel overlay window
        self.window = tk.Toplevel(self.parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-transparentcolor", self.CHROMA_KEY)
        self.window.configure(bg=self.CHROMA_KEY)
        self.window.geometry(f"{self.WINDOW_SIZE}x{self.WINDOW_SIZE}+0+0")

        self.canvas = tk.Canvas(
            self.window,
            width=self.WINDOW_SIZE,
            height=self.WINDOW_SIZE,
            bg=self.CHROMA_KEY,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.window.update_idletasks()
        try:
            self.hwnd = int(self.window.wm_frame(), 16)
        except Exception:
            self.hwnd = win32gui.GetParent(self.window.winfo_id()) or self.window.winfo_id()

        self._apply_win32_styles()

        # Start hidden
        self.window.withdraw()

    def _apply_win32_styles(self):
        try:
            gwl = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
            target_style = (
                gwl
                | win32con.WS_EX_LAYERED
                | win32con.WS_EX_TRANSPARENT  # Mouse clicks pass to windows underneath
                | win32con.WS_EX_TOOLWINDOW    # Hides from Alt-Tab
                | win32con.WS_EX_NOACTIVATE    # Never steals focus
            )
            win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, target_style)
        except Exception as e:
            print(f"[Overlay] Error applying win32 styles: {e}")

    def set_character(self, character: BaseCharacter):
        self.character = character

    def show(self, initial_x: float, initial_y: float, state: str = "wandering", facing_right: bool = True):
        """
        Positions the window and pre-renders the character at initial_x, initial_y
        BEFORE making the window visible. Guarantees zero positional jumping.
        """
        self.particles.clear()
        win_x = int(initial_x - self.WINDOW_SIZE / 2)
        win_y = int(initial_y - self.WINDOW_SIZE / 2)

        # 1. Pre-position OS window while still hidden
        win32gui.SetWindowPos(
            self.hwnd,
            win32con.HWND_TOPMOST,
            win_x,
            win_y,
            self.WINDOW_SIZE,
            self.WINDOW_SIZE,
            win32con.SWP_NOACTIVATE,
        )

        # 2. Pre-render initial frame onto canvas
        self._draw_content(win_x, win_y, state, facing_right, time.time())

        # 3. Reveal window at the exact target location
        self.window.deiconify()
        self.window.lift()
        self._apply_win32_styles()

        win32gui.SetWindowPos(
            self.hwnd,
            win32con.HWND_TOPMOST,
            win_x,
            win_y,
            self.WINDOW_SIZE,
            self.WINDOW_SIZE,
            win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW,
        )
        self.is_visible = True

    def hide(self):
        if self.is_visible:
            self.canvas.delete("all")
            self.window.withdraw()
            self.particles.clear()
            self.is_visible = False

    def render(self, x: float, y: float, state: str, facing_right: bool, time_sec: float):
        if not self.is_visible:
            return

        win_x = int(x - self.WINDOW_SIZE / 2)
        win_y = int(y - self.WINDOW_SIZE / 2)

        win32gui.SetWindowPos(
            self.hwnd,
            win32con.HWND_TOPMOST,
            win_x,
            win_y,
            self.WINDOW_SIZE,
            self.WINDOW_SIZE,
            win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW,
        )

        self._draw_content(win_x, win_y, state, facing_right, time_sec)

    def _draw_content(self, win_x: int, win_y: int, state: str, facing_right: bool, time_sec: float):
        self.canvas.delete("all")

        cx = self.WINDOW_SIZE / 2
        cy = self.WINDOW_SIZE / 2

        # 1. Particles
        if self.config.show_particles:
            self.particles.update()
            for p in self.particles.particles:
                px = p.x - win_x
                py = p.y - win_y
                if 0 <= px <= self.WINDOW_SIZE and 0 <= py <= self.WINDOW_SIZE:
                    alpha_size = max(1.0, p.size * p.life)
                    if p.kind == "circle":
                        self.canvas.create_oval(
                            px - alpha_size / 2, py - alpha_size / 2,
                            px + alpha_size / 2, py + alpha_size / 2,
                            fill=p.color, outline=""
                        )
                    elif p.kind == "star":
                        r = alpha_size
                        pts = [
                            px, py - r,
                            px + r * 0.3, py - r * 0.3,
                            px + r, py,
                            px + r * 0.3, py + r * 0.3,
                            px, py + r,
                            px - r * 0.3, py + r * 0.3,
                            px - r, py,
                            px - r * 0.3, py - r * 0.3,
                        ]
                        self.canvas.create_polygon(pts, fill=p.color, outline="")
                    elif p.kind == "text":
                        font_size = max(8, int(p.size * p.life))
                        self.canvas.create_text(
                            px, py,
                            text=p.text,
                            fill=p.color,
                            font=("Segoe UI", font_size, "bold")
                        )

        # 2. Draw character at center
        self.character.draw(
            canvas=self.canvas,
            cx=cx,
            cy=cy,
            state=state,
            facing_right=facing_right,
            time_sec=time_sec,
            scale=self.config.buddy_scale * 1.25,
            particles=self.particles if self.config.show_particles else None,
        )

        # 3. Emote reaction bubble (? or !)
        if self.config.show_reactions and state == "inspecting":
            self.canvas.create_text(
                cx + (16 if facing_right else -16),
                cy - 42 * self.config.buddy_scale,
                text="?",
                fill="#FFD700",
                font=("Segoe UI", 16, "bold"),
            )
