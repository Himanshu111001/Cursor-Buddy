"""
Lightweight particle system for visual flair and character personality.
"""

import math
import random
import time
from dataclasses import dataclass


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float  # 0.0 to 1.0 (1.0 = brand new, 0.0 = expired)
    decay_rate: float
    size: float
    color: str
    kind: str = "circle"  # 'circle', 'star', 'text', 'spark'
    text: str = ""


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def spawn_spark(self, x: float, y: float, color: str = "#00FFFF"):
        """Spawn thruster or magical spark."""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 2.5)
        p = Particle(
            x=x + random.uniform(-4, 4),
            y=y + random.uniform(-4, 4),
            vx=math.cos(angle) * speed,
            vy=math.sin(angle) * speed,
            life=1.0,
            decay_rate=random.uniform(0.04, 0.08),
            size=random.uniform(3, 7),
            color=color,
            kind="circle",
        )
        self.particles.append(p)

    def spawn_stardust(self, x: float, y: float, color: str = "#FFD700"):
        """Spawn glittering stardust."""
        p = Particle(
            x=x + random.uniform(-8, 8),
            y=y + random.uniform(-8, 8),
            vx=random.uniform(-0.5, 0.5),
            vy=random.uniform(-0.5, 0.5),
            life=1.0,
            decay_rate=random.uniform(0.03, 0.06),
            size=random.uniform(4, 9),
            color=color,
            kind="star",
        )
        self.particles.append(p)

    def spawn_sleep_bubble(self, x: float, y: float, text: str = "z"):
        """Spawn sleep Zzz bubble drifting up."""
        p = Particle(
            x=x,
            y=y,
            vx=random.uniform(0.3, 0.8),
            vy=random.uniform(-1.0, -1.8),
            life=1.0,
            decay_rate=0.025,
            size=random.uniform(11, 16),
            color="#87CEEB",
            kind="text",
            text=text,
        )
        self.particles.append(p)

    def spawn_reaction(self, x: float, y: float, text: str, color: str = "#FF69B4"):
        """Spawn reaction bubble (♥, !, ?, ✨)."""
        p = Particle(
            x=x,
            y=y,
            vx=0,
            vy=-1.2,
            life=1.0,
            decay_rate=0.02,
            size=18,
            color=color,
            kind="text",
            text=text,
        )
        self.particles.append(p)

    def update(self):
        alive = []
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.life -= p.decay_rate
            if p.life > 0:
                alive.append(p)
        self.particles = alive

    def clear(self):
        self.particles.clear()
