"""
Neko the Desktop Cat character.
A playful kitten companion with animated paws, swishing tail, and whiskers.
"""

import math
import random
import tkinter as tk
from typing import TYPE_CHECKING
from characters.base_character import BaseCharacter

if TYPE_CHECKING:
    from engine.particles import ParticleSystem


class CatCharacter(BaseCharacter):
    def __init__(self):
        super().__init__(
            name="cat",
            display_name="🐱 Neko the Desktop Cat",
            description="A playful kitten with animated paws, swishing tail, perky ears, and whiskers.",
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
        flip = 1 if facing_right else -1

        # Walking trot bob
        trot_speed = 12.0 if state == "dashing" else 7.0
        is_moving = state in ["wandering", "dashing"]
        bob_y = math.sin(time_sec * trot_speed) * (3.0 * s) if is_moving else 0.0

        xc = cx
        yc = cy + bob_y

        body_w = 34 * s
        body_h = 24 * s

        # Napping / Zzz
        if particles and state == "napping":
            if (time_sec - self.last_reaction_time) > 2.0:
                self.last_reaction_time = time_sec
                particles.spawn_sleep_bubble(xc + 18 * s * flip, yc - body_h - 6 * s, "z")

        fur_color = "#FFA07A"  # Warm ginger orange
        fur_outline = "#D35400"
        white_patch = "#FFF5EE"

        # 1. Swishing Tail (Drawn behind body)
        tail_base_x = xc - (body_w * 0.45) * flip
        tail_base_y = yc + 2 * s
        tail_swish = math.sin(time_sec * 6) * (14 * s)
        tail_pts = [
            tail_base_x, tail_base_y,
            tail_base_x - (12 * s) * flip, tail_base_y - 10 * s + tail_swish * 0.5,
            tail_base_x - (18 * s) * flip, tail_base_y - 20 * s + tail_swish,
        ]
        canvas.create_line(tail_pts, fill=fur_outline, width=max(4, int(5 * s)), smooth=True, capstyle=tk.ROUND)
        canvas.create_line(tail_pts, fill=fur_color, width=max(2, int(3 * s)), smooth=True, capstyle=tk.ROUND)

        # 2. Back Paws (animated during movement)
        paw_w = 6 * s
        paw_h = 7 * s
        for i, paw_x_offset in enumerate([-12 * s, 10 * s]):
            step = math.sin(time_sec * trot_speed + (i * math.pi)) * (4 * s) if is_moving else 0
            px = xc + paw_x_offset * flip
            py = yc + body_h / 2 - 2 * s + step
            canvas.create_oval(px - paw_w / 2, py, px + paw_w / 2, py + paw_h, fill=white_patch, outline=fur_outline, width=1)

        # 3. Main Torso
        canvas.create_oval(
            xc - body_w / 2, yc - body_h / 2,
            xc + body_w / 2, yc + body_h / 2,
            fill=fur_color, outline=fur_outline, width=max(2, int(2 * s))
        )
        # White belly patch
        canvas.create_oval(
            xc - body_w * 0.25, yc - body_h * 0.1,
            xc + body_w * 0.25, yc + body_h * 0.45,
            fill=white_patch, outline=""
        )

        # 4. Kitten Head
        head_cx = xc + (14 * s) * flip
        head_cy = yc - 6 * s
        head_r = 13 * s

        # Ears (triangles)
        for ear_flip in [-1, 1]:
            ear_bx = head_cx + (ear_flip * 7 * s)
            ear_by = head_cy - head_r * 0.7
            ear_tx = head_cx + (ear_flip * 11 * s)
            ear_ty = head_cy - head_r * 1.5
            canvas.create_polygon(
                head_cx, ear_by,
                ear_bx, ear_by,
                ear_tx, ear_ty,
                fill=fur_color, outline=fur_outline, width=1
            )
            # Inner pink ear
            canvas.create_polygon(
                head_cx, ear_by,
                head_cx + (ear_flip * 5 * s), ear_by,
                head_cx + (ear_flip * 8 * s), ear_ty + 3 * s,
                fill="#FFB6C1", outline=""
            )

        # Head circle
        canvas.create_oval(
            head_cx - head_r, head_cy - head_r,
            head_cx + head_r, head_cy + head_r,
            fill=fur_color, outline=fur_outline, width=max(2, int(2 * s))
        )

        # Eyes
        is_blinking = (time_sec % 3.8) < 0.15 or state == "napping"
        eye_ox = 3.5 * s * flip
        for ex in [head_cx - 5 * s + eye_ox, head_cx + 5 * s + eye_ox]:
            if is_blinking:
                # Closed sleeping eye
                canvas.create_line(ex - 3 * s, head_cy - 1 * s, ex + 3 * s, head_cy - 1 * s, fill="#4A2E18", width=2)
            else:
                # Big curious cat eyes
                canvas.create_oval(ex - 3.2 * s, head_cy - 4 * s, ex + 3.2 * s, head_cy + 2.5 * s, fill="#2E7D32", outline="")
                # Vertical slit pupil
                canvas.create_oval(ex - 1.2 * s, head_cy - 3.5 * s, ex + 1.2 * s, head_cy + 2.0 * s, fill="#111111", outline="")
                # Highlight
                canvas.create_oval(ex - 2.5 * s, head_cy - 3 * s, ex, head_cy - 0.5 * s, fill="#FFFFFF", outline="")

        # Cute pink nose
        nose_y = head_cy + 3 * s
        canvas.create_polygon(
            head_cx + eye_ox - 2 * s, nose_y,
            head_cx + eye_ox + 2 * s, nose_y,
            head_cx + eye_ox, nose_y + 2.5 * s,
            fill="#FF69B4", outline=""
        )

        # Whiskers
        for wy in [-1.5 * s, 1.5 * s]:
            canvas.create_line(head_cx + eye_ox + 5 * s * flip, nose_y + wy, head_cx + eye_ox + 16 * s * flip, nose_y + wy * 2, fill="#FFFFFF", width=1)
            canvas.create_line(head_cx + eye_ox - 5 * s * flip, nose_y + wy, head_cx + eye_ox - 16 * s * flip, nose_y + wy * 2, fill="#FFFFFF", width=1)
