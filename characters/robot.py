"""
Sparky the Cyber Bot character.
A playful futuristic companion with LED eyes, floating thrusters, and antenna.
"""

import math
import random
import tkinter as tk
from typing import TYPE_CHECKING
from characters.base_character import BaseCharacter

if TYPE_CHECKING:
    from engine.particles import ParticleSystem


class RobotCharacter(BaseCharacter):
    def __init__(self):
        super().__init__(
            name="robot",
            display_name="🤖 Sparky the Cyber Bot",
            description="A high-tech floating droid with glowing visor, antenna spark, and jet thrusters.",
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
        # Hover bobbing physics
        bob_speed = 7.0 if state == "dashing" else 4.0
        bob_amp = 5.0 if state == "dashing" else 3.5
        bob_y = math.sin(time_sec * bob_speed) * bob_amp

        yc = cy + bob_y
        xc = cx

        s = scale
        w, h = 36 * s, 30 * s

        # Blinking logic (every ~3.5 seconds)
        is_blinking = (time_sec % 3.5) < 0.15 or state == "napping"

        # Thrusters emission
        if particles and state != "napping":
            if random.random() < 0.45:
                thrust_color = "#00FFFF" if state != "dashing" else "#FF4500"
                particles.spawn_spark(xc - 10 * s, yc + h / 2 + 6 * s, thrust_color)
                particles.spawn_spark(xc + 10 * s, yc + h / 2 + 6 * s, thrust_color)

        if particles and state == "napping":
            if (time_sec - self.last_reaction_time) > 2.2:
                self.last_reaction_time = time_sec
                particles.spawn_sleep_bubble(xc + 16 * s, yc - h / 2 - 10 * s, "z")

        # 1. Antenna stalk & glowing beacon
        ant_x = xc + (2 * s if facing_right else -2 * s)
        ant_top_y = yc - h / 2 - 14 * s
        canvas.create_line(ant_x, yc - h / 2, ant_x, ant_top_y, fill="#708090", width=max(2, int(2.5 * s)))
        
        beacon_color = "#00FF7F" if math.sin(time_sec * 8) > 0 else "#00CED1"
        if state == "dashing":
            beacon_color = "#FF3366"
        canvas.create_oval(
            ant_x - 4 * s, ant_top_y - 4 * s,
            ant_x + 4 * s, ant_top_y + 4 * s,
            fill=beacon_color, outline="#FFFFFF", width=1
        )

        # 2. Jet Thruster Nozzles at bottom
        for tx in [xc - 11 * s, xc + 11 * s]:
            canvas.create_polygon(
                tx - 4 * s, yc + h / 2 - 2 * s,
                tx + 4 * s, yc + h / 2 - 2 * s,
                tx + 6 * s, yc + h / 2 + 5 * s,
                tx - 6 * s, yc + h / 2 + 5 * s,
                fill="#4A5568", outline="#2D3748", width=1
            )
            # Flame cone
            flame_len = (8 + math.sin(time_sec * 25 + tx) * 4) * s
            if state != "napping":
                canvas.create_polygon(
                    tx - 4 * s, yc + h / 2 + 5 * s,
                    tx + 4 * s, yc + h / 2 + 5 * s,
                    tx, yc + h / 2 + 5 * s + flame_len,
                    fill="#00E5FF", outline=""
                )

        # 3. Main Chassis Body (Rounded rectangle)
        canvas.create_rectangle(
            xc - w / 2, yc - h / 2,
            xc + w / 2, yc + h / 2,
            fill="#2B313E", outline="#4E5D6C", width=max(2, int(2 * s))
        )

        # Top chassis corner accents
        canvas.create_oval(
            xc - w / 2 - 2 * s, yc - h / 2 - 2 * s,
            xc - w / 2 + 6 * s, yc - h / 2 + 6 * s,
            fill="#4E5D6C", outline=""
        )
        canvas.create_oval(
            xc + w / 2 - 6 * s, yc - h / 2 - 2 * s,
            xc + w / 2 + 2 * s, yc - h / 2 + 6 * s,
            fill="#4E5D6C", outline=""
        )

        # 4. Visor Screen
        visor_margin_x = 4 * s
        visor_margin_y = 5 * s
        canvas.create_rectangle(
            xc - w / 2 + visor_margin_x, yc - h / 2 + visor_margin_y,
            xc + w / 2 - visor_margin_x, yc + h / 2 - visor_margin_y,
            fill="#111625", outline="#1A233A", width=1
        )

        # 5. Visor Eyes (Cyan LED lights)
        look_offset = (3.5 * s) if facing_right else (-3.5 * s)
        eye_y = yc - 1 * s

        if is_blinking:
            # Sleeping or blinking slit
            canvas.create_line(
                xc - 9 * s + look_offset, eye_y,
                xc - 3 * s + look_offset, eye_y,
                fill="#00FFFF", width=2
            )
            canvas.create_line(
                xc + 3 * s + look_offset, eye_y,
                xc + 9 * s + look_offset, eye_y,
                fill="#00FFFF", width=2
            )
        else:
            # Bright expressive oval eyes
            eye_w = 4.5 * s
            eye_h = 6.0 * s
            canvas.create_oval(
                xc - 8 * s - eye_w / 2 + look_offset, eye_y - eye_h / 2,
                xc - 8 * s + eye_w / 2 + look_offset, eye_y + eye_h / 2,
                fill="#00FFFF", outline="#E0FFFF", width=1
            )
            canvas.create_oval(
                xc + 8 * s - eye_w / 2 + look_offset, eye_y - eye_h / 2,
                xc + 8 * s + eye_w / 2 + look_offset, eye_y + eye_h / 2,
                fill="#00FFFF", outline="#E0FFFF", width=1
            )

        # 6. Floating robotic magnetic hands
        hand_bob = math.cos(time_sec * 6) * 3 * s
        left_hand_x = xc - w / 2 - 7 * s
        right_hand_x = xc + w / 2 + 7 * s
        
        canvas.create_oval(
            left_hand_x - 3.5 * s, yc - 2 * s + hand_bob,
            left_hand_x + 3.5 * s, yc + 5 * s + hand_bob,
            fill="#4E5D6C", outline="#2B313E", width=1
        )
        canvas.create_oval(
            right_hand_x - 3.5 * s, yc - 2 * s - hand_bob,
            right_hand_x + 3.5 * s, yc + 5 * s - hand_bob,
            fill="#4E5D6C", outline="#2B313E", width=1
        )
