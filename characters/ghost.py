"""
Mochi the Ghost character.
An adorable, squishy ghost companion with animated wavy skirts and kawaii expressions.
"""

import math
import random
import tkinter as tk
from typing import TYPE_CHECKING
from characters.base_character import BaseCharacter

if TYPE_CHECKING:
    from engine.particles import ParticleSystem


class GhostCharacter(BaseCharacter):
    def __init__(self):
        super().__init__(
            name="ghost",
            display_name="👻 Mochi the Ghost",
            description="A squishy, cheerful spirit with wavy floating tails, blush cheeks, and curious eyes.",
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
        # Squishy hovering motion
        hover_speed = 5.0 if state == "dashing" else 3.2
        hover_amp = 7.0 if state == "dashing" else 4.5
        hover_y = math.sin(time_sec * hover_speed) * hover_amp

        yc = cy + hover_y
        xc = cx

        # Squash and stretch
        squash = 1.0 + math.sin(time_sec * hover_speed * 2) * 0.06
        stretch = 1.0 / squash

        rad_x = 22 * s * squash
        rad_y = 26 * s * stretch

        # Sparkles emission
        if particles and random.random() < 0.25 and state != "napping":
            particles.spawn_stardust(
                xc + random.uniform(-rad_x, rad_x),
                yc + rad_y,
                color=random.choice(["#E6E6FA", "#D8BFD8", "#FFF0F5", "#B0E0E6"]),
            )

        if particles and state == "napping":
            if (time_sec - self.last_reaction_time) > 2.5:
                self.last_reaction_time = time_sec
                particles.spawn_sleep_bubble(xc + 18 * s, yc - rad_y - 8 * s, "z")

        # Head / Upper dome (oval)
        body_color = "#F4F0FF"
        outline_color = "#C3B1E1"

        canvas.create_oval(
            xc - rad_x, yc - rad_y,
            xc + rad_x, yc + rad_y * 0.4,
            fill=body_color, outline=outline_color, width=max(2, int(2 * s))
        )

        # Lower body with animated wavy ruffle skirt
        ruffle_pts = [xc - rad_x, yc]
        num_ruffles = 4
        ruffle_w = (rad_x * 2) / num_ruffles
        for i in range(num_ruffles + 1):
            rx = (xc - rad_x) + i * ruffle_w
            # Wave animation
            wave_phase = time_sec * 8 + i * 1.5
            ry = yc + rad_y * 0.9 + math.sin(wave_phase) * (4 * s)
            ruffle_pts.extend([rx, ry])

        ruffle_pts.extend([xc + rad_x, yc])
        canvas.create_polygon(ruffle_pts, fill=body_color, outline=outline_color, width=max(2, int(2 * s)))
        # Cover internal seam
        canvas.create_rectangle(xc - rad_x + 2 * s, yc - 5 * s, xc + rad_x - 2 * s, yc + 5 * s, fill=body_color, outline="")

        # Kawaii Blush marks
        blush_color = "#FFB6C1"
        canvas.create_oval(xc - rad_x * 0.7, yc + 3 * s, xc - rad_x * 0.3, yc + 9 * s, fill=blush_color, outline="")
        canvas.create_oval(xc + rad_x * 0.3, yc + 3 * s, xc + rad_x * 0.7, yc + 9 * s, fill=blush_color, outline="")

        # Eyes
        look_shift = (3 * s) if facing_right else (-3 * s)
        is_blinking = (time_sec % 4.0) < 0.15 or state == "napping"

        if is_blinking:
            # Happy smiling closed eyes ^ ^
            canvas.create_arc(
                xc - 11 * s + look_shift, yc - 4 * s,
                xc - 3 * s + look_shift, yc + 4 * s,
                start=0, extent=180, style=tk.ARC, outline="#332244", width=2
            )
            canvas.create_arc(
                xc + 3 * s + look_shift, yc - 4 * s,
                xc + 11 * s + look_shift, yc + 4 * s,
                start=0, extent=180, style=tk.ARC, outline="#332244", width=2
            )
        else:
            # Big dark anime eyes with glossy reflection
            eye_r = 4.2 * s
            for ex in [xc - 7 * s + look_shift, xc + 7 * s + look_shift]:
                canvas.create_oval(ex - eye_r, yc - eye_r, ex + eye_r, yc + eye_r, fill="#2F2542", outline="")
                # Highlights
                canvas.create_oval(ex - eye_r * 0.4, yc - eye_r * 0.6, ex + eye_r * 0.5, yc, fill="#FFFFFF", outline="")

        # Cute mouth
        if state == "inspecting":
            # Little surprised 'o'
            canvas.create_oval(xc + look_shift - 2 * s, yc + 6 * s, xc + look_shift + 2 * s, yc + 10 * s, fill="#4A3B69", outline="")
        elif state == "dashing":
            # Excited open smile
            canvas.create_arc(xc + look_shift - 5 * s, yc + 3 * s, xc + look_shift + 5 * s, yc + 9 * s, start=180, extent=180, fill="#FF6B81", outline="")
        else:
            # Gentle smile
            canvas.create_arc(xc + look_shift - 3.5 * s, yc + 5 * s, xc + look_shift + 3.5 * s, yc + 9 * s, start=180, extent=180, style=tk.ARC, outline="#4A3B69", width=2)
