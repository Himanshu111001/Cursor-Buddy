"""
Transparent click-through overlay window for Windows desktop.
Renders the animated character and visual particles without interrupting user workflow.
"""

import math
import tkinter as tk
import win32api
import win32con
import win32gui
from characters.base_character import BaseCharacter
from config import BuddyConfig
from engine.particles import ParticleSystem


class OverlayWindow:
    CHROMA_KEY = "#010101"  # Deep black color used as transparent background

    def __init__(self, root: tk.Tk, config: BuddyConfig, character: BaseCharacter, particles: ParticleSystem):
        self.root = root
        self.config = config
        self.character = character
        self.particles = particles
        self.is_visible = False

        # Virtual screen metrics for single or multi-monitor setups
        self.vx = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        self.vy = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        self.vw = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        self.vh = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

        # Configure root as a borderless transparent overlay
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", self.CHROMA_KEY)
        self.root.geometry(f"{self.vw}x{self.vh}+{self.vx}+{self.vy}")

        # High-performance canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.vw,
            height=self.vh,
            bg=self.CHROMA_KEY,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # Apply native Windows extended styles (Click-through, No Alt-Tab, No Focus Steal)
        self._apply_win32_styles()

        # Start hidden
        self.root.withdraw()

    def _apply_win32_styles(self):
        hwnd = self.root.winfo_id()
        gwl = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        target_style = (
            gwl
            | win32con.WS_EX_LAYERED
            | win32con.WS_EX_TRANSPARENT  # Passes all mouse clicks through to whatever is underneath
            | win32con.WS_EX_TOOLWINDOW    # Hides from Alt-Tab task switcher
            | win32con.WS_EX_NOACTIVATE    # Prevents stealing keyboard/window focus
        )
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, target_style)

    def set_character(self, character: BaseCharacter):
        self.character = character

    def show(self):
        if not self.is_visible:
            self.root.deiconify()
            self.root.lift()
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

        self.canvas.delete("all")

        # Convert virtual screen coordinates to canvas local coordinates
        canvas_x = x - self.vx
        canvas_y = y - self.vy

        # 1. Update and draw particles
        if self.config.show_particles:
            self.particles.update()
            for p in self.particles.particles:
                px = p.x - self.vx
                py = p.y - self.vy
                alpha_size = max(1.0, p.size * p.life)

                if p.kind == "circle":
                    self.canvas.create_oval(
                        px - alpha_size / 2, py - alpha_size / 2,
                        px + alpha_size / 2, py + alpha_size / 2,
                        fill=p.color, outline=""
                    )
                elif p.kind == "star":
                    # Draw sparkling 4-pointed star
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

        # 2. Draw active character
        self.character.draw(
            canvas=self.canvas,
            cx=canvas_x,
            cy=canvas_y,
            state=state,
            facing_right=facing_right,
            time_sec=time_sec,
            scale=self.config.buddy_scale,
            particles=self.particles if self.config.show_particles else None,
        )

        # 3. Optional status bubble (e.g. state reactions)
        if self.config.show_reactions and state == "inspecting":
            bubble_y = canvas_y - 45 * self.config.buddy_scale
            self.canvas.create_text(
                canvas_x + (16 if facing_right else -16),
                bubble_y,
                text="?",
                fill="#FFD700",
                font=("Segoe UI", 16, "bold"),
            )
