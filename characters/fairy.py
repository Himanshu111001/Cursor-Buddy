"""
Starlight Fairy / Sparkle Orb character.
A luminous magical companion with fluttering iridescent wings, glowing aura, and star trails.
"""

import math
import random
import tkinter as tk
from typing import TYPE_CHECKING
from characters.base_character import BaseCharacter

if TYPE_CHECKING:
    from engine.particles import ParticleSystem


class FairyCharacter(BaseCharacter):
    def __init__(self):
        super().__init__(
            name="fairy",
            display_name="🧚 Starlight Fairy",
            description="A luminous magical fairy with fluttering gossamer wings, glowing aura, and stardust trails.",
        )

    def draw(
        self,
        canvas: tk.Canvas,
        cx: float,
        cy: float,
        state: str,
        facing_right: bool,
        time_sec: float,
        scale: float = 1.0,
        particles: ParticleSystem | None = None,
    ):
        s = scale
        # Fluid floating motion
        float_y = math.sin(time_sec * 5.0) * (5.0 * s)
        float_x = math.cos(time_sec * 3.5) * (3.0 * s)
        xc = cx + float_x
        yc = cy + float_y

        # Emitting magical stardust trail
        if particles and random.random() < 0.6:
            color = random.choice(["#FFE4B5", "#FFD700", "#E0FFFF", "#FFB6C1", "#FFFACD"])
            particles.spawn_stardust(xc + random.uniform(-6, 6), yc + random.uniform(-6, 6), color=color)

        if particles and state == "napping":
            if (time_sec - self.last_reaction_time) > 2.0:
                self.last_reaction_time = time_sec
                particles.spawn_sleep_bubble(xc + 14 * s, yc - 16 * s, "✨")

        # 1. Fluttering Gossamer Wings (Fast flutter rate)
        wing_flutter = math.sin(time_sec * 24.0)
        wing_w = (18 * s) * (0.3 + 0.7 * abs(wing_flutter))
        wing_h = 24 * s

        wing_color = "#E0FFFF"
        wing_edge = "#B0E0E6"

        # Top wings
        canvas.create_oval(
            xc - 6 * s - wing_w, yc - wing_h,
            xc - 2 * s, yc + 2 * s,
            fill=wing_color, outline=wing_edge, width=1
        )
        canvas.create_oval(
            xc + 2 * s, yc - wing_h,
            xc + 6 * s + wing_w, yc + 2 * s,
            fill=wing_color, outline=wing_edge, width=1
        )

        # Bottom mini wings
        canvas.create_oval(
            xc - 4 * s - wing_w * 0.7, yc - 2 * s,
            xc - 1 * s, yc + wing_h * 0.7,
            fill=wing_color, outline=wing_edge, width=1
        )
        canvas.create_oval(
            xc + 1 * s, yc - 2 * s,
            xc + 4 * s + wing_w * 0.7, yc + wing_h * 0.7,
            fill=wing_color, outline=wing_edge, width=1
        )

        # 2. Glowing Outer Halo / Aura
        halo_r = (18 + math.sin(time_sec * 6) * 2) * s
        canvas.create_oval(
            xc - halo_r, yc - halo_r,
            xc + halo_r, yc + halo_r,
            fill="#FFF8DC", outline="#FFD700", width=1
        )

        # 3. Radiant Core Orb
        core_r = 12 * s
        canvas.create_oval(
            xc - core_r, yc - core_r,
            xc + core_r, yc + core_r,
            fill="#FFFFE0", outline="#FFA500", width=max(2, int(2 * s))
        )

        # Inner hot white sparkle
        inner_r = 6 * s
        canvas.create_oval(
            xc - inner_r, yc - inner_r,
            xc + inner_r, yc + inner_r,
            fill="#FFFFFF", outline=""
        )

        # Cute cheerful twinkling eyes
        look_ox = (2.5 * s) if facing_right else (-2.5 * s)
        is_blinking = (time_sec % 3.2) < 0.15 or state == "napping"
        if is_blinking:
            canvas.create_line(xc - 4 * s + look_ox, yc, xc - 1 * s + look_ox, yc, fill="#B8860B", width=2)
            canvas.create_line(xc + 1 * s + look_ox, yc, xc + 4 * s + look_ox, yc, fill="#B8860B", width=2)
        else:
            canvas.create_oval(xc - 4 * s + look_ox, yc - 2 * s, xc - 1 * s + look_ox, yc + 2 * s, fill="#8B6508", outline="")
            canvas.create_oval(xc + 1 * s + look_ox, yc - 2 * s, xc + 4 * s + look_ox, yc + 2 * s, fill="#8B6508", outline="")
