"""
Autonomous movement and behavioral AI engine for the desktop companion.
Generates organic, entertaining trajectories, curiosity pauses, and playful behaviors.
"""

import math
import random
import time


class MovementEngine:
    # Behavioral states
    STATE_WANDERING = "wandering"
    STATE_INSPECTING = "inspecting"
    STATE_DASHING = "dashing"
    STATE_NAPPING = "napping"

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.margin = 60

        # Current position & physics
        self.x = screen_w / 2.0
        self.y = screen_h / 2.0
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
        self.base_speed = 4.5
        self.set_speed_profile("normal")

    def set_speed_profile(self, profile: str):
        if profile == "slow":
            self.base_speed = 2.5
        elif profile == "fast":
            self.base_speed = 7.5
        else:  # normal
            self.base_speed = 4.5

    def reset_to_position(self, x: float, y: float):
        """Reset companion to a specific position (e.g. current mouse position)."""
        self.x = min(max(x, self.margin), self.screen_w - self.margin)
        self.y = min(max(y, self.margin), self.screen_h - self.margin)
        self.vx = 0.0
        self.vy = 0.0
        self.state = self.STATE_WANDERING
        self.state_timer = 0.0
        self.total_idle_time = 0.0
        self._pick_new_target()

    def _pick_new_target(self):
        """Pick an engaging destination on screen."""
        dice = random.random()
        if dice < 0.25:
            # Peek near a corner or screen edge
            corner_x = random.choice([self.margin + 40, self.screen_w - self.margin - 40])
            corner_y = random.choice([self.margin + 40, self.screen_h - self.margin - 40])
            self.target_x = corner_x + random.uniform(-20, 20)
            self.target_y = corner_y + random.uniform(-20, 20)
        else:
            # Wander anywhere within comfortable desktop bounds
            self.target_x = random.uniform(self.margin, self.screen_w - self.margin)
            self.target_y = random.uniform(self.margin, self.screen_h - self.margin)

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
            self._step_towards_target(max_speed=self.base_speed * 1.8)
        elif self.state == self.STATE_INSPECTING:
            # Gently decelerate and look around
            self.vx *= 0.85
            self.vy *= 0.85
        elif self.state == self.STATE_NAPPING:
            # Stay nearly still with a gentle breathing rhythm
            self.vx *= 0.80
            self.vy *= 0.80

        # Apply velocity
        self.x += self.vx
        self.y += self.vy

        # Keep strictly within screen bounds
        self.x = min(max(self.x, self.margin), self.screen_w - self.margin)
        self.y = min(max(self.y, self.margin), self.screen_h - self.margin)

        # Update facing direction
        if abs(self.vx) > 0.2:
            self.facing_right = self.vx > 0

        return self.x, self.y, self.state

    def _step_towards_target(self, max_speed: float):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < 35:
            # Close enough to target, decide next move
            self.state = self.STATE_INSPECTING
            self.state_timer = 0.0
            self.state_duration = random.uniform(1.2, 2.5)
            self._pick_new_target()
            return

        # Desired velocity vector (steering towards target)
        desired_vx = (dx / dist) * max_speed
        desired_vy = (dy / dist) * max_speed

        # Smooth acceleration steering (lerp velocity)
        steer_rate = 0.12
        self.vx += (desired_vx - self.vx) * steer_rate
        self.vy += (desired_vy - self.vy) * steer_rate

    def _transition_state(self):
        self.state_timer = 0.0
        # If idle for a long time (> 35s), character has a chance to nap
        if self.total_idle_time > 35.0 and random.random() < 0.4:
            self.state = self.STATE_NAPPING
            self.state_duration = random.uniform(5.0, 9.0)
            return

        # Choose next playful action
        choice = random.random()
        if choice < 0.55:
            self.state = self.STATE_WANDERING
            self.state_duration = random.uniform(2.5, 5.0)
        elif choice < 0.80:
            self.state = self.STATE_INSPECTING
            self.state_duration = random.uniform(1.5, 3.0)
        else:
            self.state = self.STATE_DASHING
            self.state_duration = random.uniform(1.0, 2.0)
            self._pick_new_target()
