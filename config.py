"""
Configuration manager for Animated Cursor Buddy.
Persists user preferences to a local JSON file.
"""

import json
import os
from dataclasses import asdict, dataclass

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


@dataclass
class BuddyConfig:
    idle_timeout_seconds: int = 10
    character: str = "robot"  # 'robot', 'ghost', 'cat', 'fairy'
    movement_speed: str = "normal"  # 'slow', 'normal', 'fast'
    move_physical_cursor: bool = True
    keep_screen_awake: bool = True
    show_particles: bool = True
    show_reactions: bool = True
    sound_enabled: bool = False
    buddy_scale: float = 1.0  # 0.8x to 1.5x

    @classmethod
    def load(cls) -> "BuddyConfig":
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            except Exception as e:
                print(f"[Config] Error loading config: {e}. Using defaults.")
        config = cls()
        config.save()
        return config

    def save(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=4)
        except Exception as e:
            print(f"[Config] Error saving config: {e}")
