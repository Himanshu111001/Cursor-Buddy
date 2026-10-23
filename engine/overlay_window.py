"""
Compact floating transparent sprite overlay window.
Moves seamlessly with the companion at hardware level without full-screen flicker.
"""

import math
import tkinter as tk
import win32con
import win32gui
from characters.base_character import BaseCharacter
from config import BuddyConfig
from engine.particles import ParticleSystem


class OverlayWindow:
    CHROMA_KEY = "#010101"
    WINDOW_SIZE = 128  # Compact 128x128 sprite box

    def __init__(self, root: tk.Tk, config: BuddyConfig, character: BaseCharacter, particles: ParticleSystem):
        self.root = root
        self.config = config
        self.character = character
        self.particles = particles
        self.is_visible = False

        # Borderless transparent sprite window
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", self.CHROMA_KEY)
        self.root.geometry(f"{self.WINDOW_SIZE}x{self.WINDOW_SIZE}+0+0")

        self.canvas = tk.Canvas(
            self.root,
            width=self.WINDOW_SIZE,
            height=self.WINDOW_SIZE,
            bg=self.CHROMA_KEY,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self._hwnd = self.root.winfo_id()
        self._apply_win32_styles()

        # Start hidden
        self.root.withdraw()

    def _apply_win32_styles(self):
        hwnd = self.root.winfo_id()
        gwl = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        target_style = (
            gwl
            | win32con.WS_EX_LAYERED
            | win32con.WS_EX_TRANSPARENT  # Click-through: mouse clicks pass to whatever is beneath
            | win32con.WS_EX_TOOLWINDOW    # Hides from Alt-Tab
            | win32con.WS_EX_NOACTIVATE    # Never steals keyboard/mouse focus
        )
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, target_style)

    def set_character(self, character: BaseCharacter):
        self.character = character

    def show(self):
        if not self.is_visible:
            self.root.deiconify()
            self._apply_win32_styles()
            self.is_visible = True

    def hide(self):
        if self.is_visible:
            self.canvas.delete("all")
            self.root.withdraw()
            self.particles.clear()
            self.is_visible = False

    def render(self, x: float, y: float, state: str, facing_right: bool, time_sec: float):
        if not self.is_visible:
            return

        # Position the 128x128 window directly centered on the companion coordinate
        win_x = int(x - self.WINDOW_SIZE / 2)
        win_y = int(y - self.WINDOW_SIZE / 2)

        win32gui.SetWindowPos(
            self.root.winfo_id(),
            win32con.HWND_TOPMOST,
            win_x,
            win_y,
            0,
            0,
            win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW,
        )

        self.canvas.delete("all")

        # Center inside the 128x128 canvas
        cx = self.WINDOW_SIZE / 2
        cy = self.WINDOW_SIZE / 2

        # 1. Particles (rendered relative to center)
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

        # 2. Draw Character at center
        self.character.draw(
            canvas=self.canvas,
            cx=cx,
            cy=cy,
            state=state,
            facing_right=facing_right,
            time_sec=time_sec,
            scale=self.config.buddy_scale,
            particles=self.particles if self.config.show_particles else None,
        )

        # 3. Emote reaction bubble (? or !)
        if self.config.show_reactions and state == "inspecting":
            self.canvas.create_text(
                cx + (14 if facing_right else -14),
                cy - 38 * self.config.buddy_scale,
                text="?",
                fill="#FFD700",
                font=("Segoe UI", 15, "bold"),
            )
