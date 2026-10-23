"""
Base abstract class for all Animated Cursor Buddies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import tkinter as tk

if TYPE_CHECKING:
    from engine.particles import ParticleSystem


class BaseCharacter(ABC):
    def __init__(self, name: str, display_name: str, description: str):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.last_blink_time = 0.0
        self.last_reaction_time = 0.0

    @abstractmethod
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
        """
        Draw the character on the canvas at (cx, cy).
        canvas: Tkinter Canvas
        cx, cy: Center coordinate
        state: Movement state ('wandering', 'inspecting', 'dashing', 'napping')
        facing_right: Direction facing
        time_sec: Current running timestamp for procedural animations
        scale: Size scale multiplier
        particles: Optional ParticleSystem to emit particles into
        """
        pass
