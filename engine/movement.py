"""
Autonomous movement and behavioral AI engine for the desktop companion.
Maintains smooth organic trajectories and zero-offset resets upon idle activation.
"""

import math
import random


class MovementEngine:
    # Behavioral states
    STATE_WANDERING = "wandering"
    STATE_INSPECTING = "inspecting"
    STATE_DASHING = "dashing"
    STATE_NAPPING = "napping"

    def __init__(self, bounds: tuple[int, int, int, int]):
        """
        bounds: (left, top, right, bottom) of usable work area (excluding taskbar).
        """
        self.set_bounds(bounds)

        # Current position & physics
        self.x = (self.min_x + self.max_x) / 2.0
        self.y = (self.min_y + self.max_y) / 2.0
        self.vx = 0.0
        self.vy = 0.0
        self.facing_right = True
        self.wobble_time = 0.0

        # Target waypoint
        self.target_x = self.x
        self.target_y = self.y

        # State management
        self.state = self.STATE_WANDERING
        self.state_timer = 0.0
        self.state_duration = 3.0
        self.total_idle_time = 0.0

        # Speed configurations
        self.base_speed = 3.8
        self.set_speed_profile("normal")

    def set_bounds(self, bounds: tuple[int, int, int, int]):
        left, top, right, bottom = bounds
        self.bounds_left = left
        self.bounds_top = top
        self.bounds_right = right
        self.bounds_bottom = bottom

        self.margin = 55  # Safe distance for waypoints inside bezels and above taskbar
        self.min_x = left + self.margin
        self.min_y = top + self.margin
        self.max_x = max(self.min_x + 100, right - self.margin)
        self.max_y = max(self.min_y + 100, bottom - self.margin)

    def set_speed_profile(self, profile: str):
        if profile == "slow":
            self.base_speed = 2.2
        elif profile == "fast":
            self.base_speed = 6.5
        else:  # normal
            self.base_speed = 3.8

    def reset_to_position(self, x: float, y: float):
        """
        Aligns companion position directly with the current physical mouse coordinates.
        Does not clamp to interior margin to prevent sudden jumping upon wake.
        """
        # Guard strictly against off-screen bounds while keeping exact mouse coordinates
        self.x = min(max(float(x), self.bounds_left), self.bounds_right)
        self.y = min(max(float(y), self.bounds_top), self.bounds_bottom)
        self.vx = 0.0
        self.vy = 0.0
        self.state = self.STATE_WANDERING
        self.state_timer = 0.0
        self.total_idle_time = 0.0
        self._pick_new_target()

    def _pick_new_target(self):
        """Pick an engaging destination strictly within comfortable screen bounds."""
        dice = random.random()
        if dice < 0.25:
            # Corner inspection point
            corner_x = random.choice([self.min_x + 25, self.max_x - 25])
            corner_y = random.choice([self.min_y + 25, self.max_y - 25])
            self.target_x = min(max(corner_x + random.uniform(-15, 15), self.min_x), self.max_x)
            self.target_y = min(max(corner_y + random.uniform(-15, 15), self.min_y), self.max_y)
        else:
            # Wander anywhere inside work area
            self.target_x = random.uniform(self.min_x, self.max_x)
            self.target_y = random.uniform(self.min_y, self.max_y)

    def update(self, dt: float) -> tuple[float, float, str]:
        """
        Updates AI movement and behavior state.
        Returns: (x, y, current_state)
        """
        self.wobble_time += dt
        self.state_timer += dt
        self.total_idle_time += dt

        # State transition logic
        if self.state_timer >= self.state_duration:
            self._transition_state()

        # Execute current state behavior
        if self.state == self.STATE_WANDERING:
            self._step_towards_target(max_speed=self.base_speed)
        elif self.state == self.STATE_DASHING:
            self._step_towards_target(max_speed=self.base_speed * 1.6)
        elif self.state == self.STATE_INSPECTING:
            self.vx *= 0.85
            self.vy *= 0.85
        elif self.state == self.STATE_NAPPING:
            self.vx *= 0.80
            self.vy *= 0.80

        # Apply velocity
        self.x += self.vx
        self.y += self.vy

        # Confine strictly within screen work area
        self.x = min(max(self.x, self.bounds_left), self.bounds_right)
        self.y = min(max(self.y, self.bounds_top), self.bounds_bottom)

        # Update facing direction
        if abs(self.vx) > 0.2:
            self.facing_right = self.vx > 0

        return self.x, self.y, self.state

    def _step_towards_target(self, max_speed: float):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < 25:
            self.state = self.STATE_INSPECTING
            self.state_timer = 0.0
            self.state_duration = random.uniform(1.2, 2.5)
            self._pick_new_target()
            return

        desired_vx = (dx / dist) * max_speed
        desired_vy = (dy / dist) * max_speed

        steer_rate = 0.12
        self.vx += (desired_vx - self.vx) * steer_rate
        self.vy += (desired_vy - self.vy) * steer_rate

    def _transition_state(self):
        self.state_timer = 0.0
        # If idle for an extended period, chance to nap
        if self.total_idle_time > 35.0 and random.random() < 0.4:
            self.state = self.STATE_NAPPING
            self.state_duration = random.uniform(5.0, 9.0)
            return

        choice = random.random()
        if choice < 0.55:
            self.state = self.STATE_WANDERING
            self.state_duration = random.uniform(2.5, 4.5)
        elif choice < 0.80:
            self.state = self.STATE_INSPECTING
            self.state_duration = random.uniform(1.5, 3.0)
        else:
            self.state = self.STATE_DASHING
            self.state_duration = random.uniform(1.0, 2.0)
            self._pick_new_target()
