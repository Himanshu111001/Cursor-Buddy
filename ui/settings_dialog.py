"""
Modern, sleek, premium Settings & Customization Dialog for Animated Cursor Buddy.
Engineered with Fluent / macOS design language: custom switches, sliders,
segmented controls, character cards, DWM dark mode, and high-DPI scaling.
"""

from __future__ import annotations

import os
import tkinter as tk
from characters import CHARACTERS, get_character
from config import BuddyConfig
from system import get_desktop_work_area, is_autostart_enabled, set_autostart
from ui.modern_widgets import (
    PALETTE,
    CompanionCard,
    CompactToggleRow,
    ModernButton,
    ModernSlider,
    SegmentedPill,
    apply_dwm_dark_theme,
    draw_rounded_rect,
)


class SettingsDialog:
    def __init__(self, parent: tk.Tk, config: BuddyConfig, on_save_callback, on_test_callback):
        self.parent = parent
        self.config = config
        self.on_save = on_save_callback
        self.on_test = on_test_callback
        self.window: tk.Toplevel | None = None
        self.preview_character = get_character(self.config.character)
        self.preview_time = 0.0
        self._is_preview_running = False
        self.char_cards: dict[str, CompanionCard] = {}

    def show(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()
            self.window.attributes("-topmost", True)
            self.window.after_idle(lambda: self.window.attributes("-topmost", False))
            self.window.focus_force()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Animated Cursor Buddy")

        # Dimensions designed for optimal breathing room and high-DPI display compatibility
        win_w, win_h = 560, 650
        self.window.geometry(f"{win_w}x{win_h}")
        self.window.resizable(False, False)
        self.window.configure(bg=PALETTE["bg_window"])
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Center inside desktop work area
        left, top, right, bottom = get_desktop_work_area()
        pos_x = left + ((right - left) - win_w) // 2
        pos_y = top + ((bottom - top) - win_h) // 2
        self.window.geometry(f"+{max(10, pos_x)}+{max(10, pos_y)}")

        # App Icon
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.window.iconbitmap(icon_path)
            except Exception:
                pass

        # Apply Windows 11 DWM immersive dark mode to title bar
        apply_dwm_dark_theme(self.window, PALETTE["bg_window"])

        self._build_ui()
        self._is_preview_running = True
        self._run_preview_loop()

    def _build_ui(self):
        # 1. Header Row
        header = tk.Frame(self.window, bg=PALETTE["bg_window"])
        header.pack(fill="x", padx=18, pady=(10, 6))

        title_col = tk.Frame(header, bg=PALETTE["bg_window"])
        title_col.pack(side="left")

        title_row = tk.Frame(title_col, bg=PALETTE["bg_window"])
        title_row.pack(anchor="w")

        tk.Label(
            title_row,
            text="✨ Cursor Buddy",
            font=("Segoe UI", 12, "bold"),
            fg=PALETTE["text_main"],
            bg=PALETTE["bg_window"],
        ).pack(side="left")

        tk.Label(
            title_row,
            text=" Control Center",
            font=("Segoe UI", 12, "normal"),
            fg=PALETTE["text_muted"],
            bg=PALETTE["bg_window"],
        ).pack(side="left")

        # Shortcut Pill Badge
        badge_frame = tk.Frame(
            header,
            bg=PALETTE["bg_card_inner"],
            highlightbackground=PALETTE["border"],
            highlightthickness=1,
            padx=8,
            pady=3,
        )
        badge_frame.pack(side="right")

        tk.Label(
            badge_frame,
            text="⚡ Ctrl + Alt + B",
            font=("Segoe UI", 8, "bold"),
            fg=PALETTE["accent_glow"],
            bg=PALETTE["bg_card_inner"],
        ).pack()

        # 2. Live Character Preview Card
        preview_container = tk.Frame(
            self.window,
            bg=PALETTE["bg_card"],
            highlightbackground=PALETTE["border"],
            highlightthickness=1,
        )
        preview_container.pack(fill="x", padx=18, pady=(0, 8))

        self.preview_canvas = tk.Canvas(
            preview_container,
            width=522,
            height=70,
            bg="#10121B",
            highlightthickness=0,
            bd=0,
        )
        self.preview_canvas.pack(fill="both", expand=True)

        # 3. Companion Selector
        char_section = tk.Frame(self.window, bg=PALETTE["bg_window"])
        char_section.pack(fill="x", padx=18, pady=(0, 8))

        tk.Label(
            char_section,
            text="CHOOSE COMPANION",
            font=("Segoe UI", 7, "bold"),
            fg=PALETTE["text_dim"],
            bg=PALETTE["bg_window"],
        ).pack(anchor="w", pady=(0, 4))

        grid = tk.Frame(char_section, bg=PALETTE["bg_window"])
        grid.pack(fill="x")

        self.selected_char = self.config.character
        char_options = [
            ("robot", "Sparky", "Cyber Bot"),
            ("ghost", "Mochi", "Squishy Ghost"),
            ("cat", "Neko", "Playful Kitten"),
            ("fairy", "Fairy", "Starlight Aura"),
        ]

        self.char_cards = {}
        for i, (key, name, persona) in enumerate(char_options):
            card = CompanionCard(
                grid,
                char_key=key,
                name=name,
                persona=persona,
                character_instance=get_character(key),
                is_selected=(key == self.selected_char),
                on_click=self._select_char,
                width=123,
                height=66,
            )
            card.pack(side="left", fill="x", expand=True, padx=(0 if i == 0 else 6, 0))
            self.char_cards[key] = card

        # 4. Motion & Behavior Card (Slider + Speed pills)
        behavior_card = tk.Frame(
            self.window,
            bg=PALETTE["bg_card"],
            highlightbackground=PALETTE["border"],
            highlightthickness=1,
            padx=12,
            pady=8,
        )
        behavior_card.pack(fill="x", padx=18, pady=(0, 8))

        # Row A: Idle Delay Slider
        slider_header = tk.Frame(behavior_card, bg=PALETTE["bg_card"])
        slider_header.pack(fill="x", pady=(0, 2))

        tk.Label(
            slider_header,
            text="Idle Activation Delay",
            font=("Segoe UI", 8, "bold"),
            fg=PALETTE["text_main"],
            bg=PALETTE["bg_card"],
        ).pack(side="left")

        self.timeout_var = tk.IntVar(value=self.config.idle_timeout_seconds)
        self.timeout_badge = tk.Label(
            slider_header,
            text=f"{self.timeout_var.get()}s",
            font=("Segoe UI", 8, "bold"),
            fg=PALETTE["accent_glow"],
            bg=PALETTE["bg_card_inner"],
            padx=6,
            pady=1,
        )
        self.timeout_badge.pack(side="right")

        self.timeout_slider = ModernSlider(
            behavior_card,
            variable=self.timeout_var,
            from_=3,
            to=60,
            command=lambda v: self.timeout_badge.config(text=f"{v}s"),
            bg=PALETTE["bg_card"],
            accent=PALETTE["accent"],
        )
        self.timeout_slider.pack(fill="x", pady=(1, 5))

        # Row B: Wander Speed Segmented Control
        speed_header = tk.Frame(behavior_card, bg=PALETTE["bg_card"])
        speed_header.pack(fill="x", pady=(0, 2))

        tk.Label(
            speed_header,
            text="Wander Speed",
            font=("Segoe UI", 8, "bold"),
            fg=PALETTE["text_main"],
            bg=PALETTE["bg_card"],
        ).pack(side="left")

        self.speed_var = tk.StringVar(value=self.config.movement_speed)
        speed_options = [
            ("slow", "Slow", "🐢"),
            ("normal", "Normal", "⚡"),
            ("fast", "Fast", "🚀"),
        ]
        self.speed_segmented = SegmentedPill(
            behavior_card,
            variable=self.speed_var,
            options=speed_options,
            bg=PALETTE["bg_card"],
        )
        self.speed_segmented.pack(fill="x")

        # 5. Features & Preferences (Two clean side-by-side cards)
        toggles_container = tk.Frame(self.window, bg=PALETTE["bg_window"])
        toggles_container.pack(fill="x", padx=18, pady=(0, 10))

        # State Variables
        self.move_cursor_var = tk.BooleanVar(value=self.config.move_physical_cursor)
        self.hide_cursor_var = tk.BooleanVar(value=self.config.hide_default_cursor)
        self.keep_awake_var = tk.BooleanVar(value=self.config.keep_screen_awake)
        self.particles_var = tk.BooleanVar(value=self.config.show_particles)
        self.pause_media_var = tk.BooleanVar(value=self.config.pause_during_media)
        self.pause_fullscreen_var = tk.BooleanVar(value=self.config.pause_on_fullscreen)
        self.sound_var = tk.BooleanVar(value=self.config.sound_enabled)
        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())

        # Column 1: Pointer & Display Card
        col1_card = tk.Frame(
            toggles_container,
            bg=PALETTE["bg_card"],
            highlightbackground=PALETTE["border"],
            highlightthickness=1,
            padx=2,
            pady=3,
        )
        col1_card.pack(side="left", fill="both", expand=True, padx=(0, 4))

        tk.Label(
            col1_card,
            text="POINTER & DISPLAY",
            font=("Segoe UI", 7, "bold"),
            fg=PALETTE["text_dim"],
            bg=PALETTE["bg_card"],
        ).pack(anchor="w", padx=6, pady=(1, 2))

        CompactToggleRow(
            col1_card,
            icon="🖱️",
            title="Guide Cursor",
            variable=self.move_cursor_var,
        ).pack(fill="x", pady=1)

        CompactToggleRow(
            col1_card,
            icon="👁️",
            title="Hide Native Pointer",
            variable=self.hide_cursor_var,
        ).pack(fill="x", pady=1)

        CompactToggleRow(
            col1_card,
            icon="☕",
            title="Keep Screen Awake",
            variable=self.keep_awake_var,
        ).pack(fill="x", pady=1)

        CompactToggleRow(
            col1_card,
            icon="✨",
            title="Particle FX",
            variable=self.particles_var,
        ).pack(fill="x", pady=1)

        # Column 2: System & Detection Card
        col2_card = tk.Frame(
            toggles_container,
            bg=PALETTE["bg_card"],
            highlightbackground=PALETTE["border"],
            highlightthickness=1,
            padx=2,
            pady=3,
        )
        col2_card.pack(side="right", fill="both", expand=True, padx=(4, 0))

        tk.Label(
            col2_card,
            text="SMART DETECTION & AUDIO",
            font=("Segoe UI", 7, "bold"),
            fg=PALETTE["text_dim"],
            bg=PALETTE["bg_card"],
        ).pack(anchor="w", padx=6, pady=(1, 2))

        CompactToggleRow(
            col2_card,
            icon="🎬",
            title="Pause on Media",
            variable=self.pause_media_var,
        ).pack(fill="x", pady=1)

        CompactToggleRow(
            col2_card,
            icon="🎮",
            title="Pause in Fullscreen",
            variable=self.pause_fullscreen_var,
        ).pack(fill="x", pady=1)

        CompactToggleRow(
            col2_card,
            icon="🔔",
            title="Audio Chimes",
            variable=self.sound_var,
        ).pack(fill="x", pady=1)

        CompactToggleRow(
            col2_card,
            icon="🚀",
            title="Start with Windows",
            variable=self.autostart_var,
        ).pack(fill="x", pady=1)

        # 6. Bottom Action Bar
        btn_bar = tk.Frame(self.window, bg=PALETTE["bg_window"])
        btn_bar.pack(fill="x", padx=18, pady=(0, 14))

        ModernButton(
            btn_bar,
            text="🚀 Summon Now",
            command=self._handle_test,
            width=150,
            height=36,
            is_primary=False,
        ).pack(side="left")

        ModernButton(
            btn_bar,
            text="✓ Save & Apply",
            command=self._handle_save,
            width=160,
            height=36,
            is_primary=True,
        ).pack(side="right")

    def _select_char(self, char_key: str):
        self.selected_char = char_key
        self.preview_character = get_character(char_key)
        for k, card in self.char_cards.items():
            card.set_selected(k == char_key)

    def _run_preview_loop(self):
        if not self._is_preview_running or not self.window or not self.window.winfo_exists():
            return

        self.preview_time += 0.033
        self.preview_canvas.delete("all")

        w = 522
        h = 70
        cx = w / 2.0
        cy = h / 2.0 + 1

        # Ambient radial glow behind companion
        self.preview_canvas.create_oval(
            cx - 60, cy - 28, cx + 60, cy + 28, fill="#151826", outline=""
        )
        self.preview_canvas.create_oval(
            cx - 36, cy - 16, cx + 36, cy + 16, fill="#1C2138", outline=""
        )

        # Subtle dark dots grid
        for gx in range(24, w, 28):
            for gy in range(10, h, 20):
                self.preview_canvas.create_oval(gx - 1, gy - 1, gx + 1, gy + 1, fill="#191C29", outline="")

        # LIVE PREVIEW Pill Badge in top right
        self.preview_canvas.create_oval(w - 105, 10, w - 99, 16, fill=PALETTE["accent_cyan"], outline="")
        self.preview_canvas.create_text(
            w - 52,
            13,
            text="LIVE PREVIEW",
            font=("Segoe UI", 7, "bold"),
            fill=PALETTE["text_dim"],
        )

        # Render preview character centered
        self.preview_character.draw(
            canvas=self.preview_canvas,
            cx=cx,
            cy=cy,
            state="wandering",
            facing_right=True,
            time_sec=self.preview_time,
            scale=0.95,
            particles=None,
        )

        self.window.after(33, self._run_preview_loop)

    def _handle_save(self):
        self.config.character = self.selected_char
        self.config.idle_timeout_seconds = self.timeout_var.get()
        self.config.movement_speed = self.speed_var.get()
        self.config.move_physical_cursor = self.move_cursor_var.get()
        self.config.hide_default_cursor = self.hide_cursor_var.get()
        self.config.keep_screen_awake = self.keep_awake_var.get()
        self.config.show_particles = self.particles_var.get()
        self.config.sound_enabled = self.sound_var.get()
        self.config.pause_during_media = self.pause_media_var.get()
        self.config.pause_on_fullscreen = self.pause_fullscreen_var.get()

        should_autostart = self.autostart_var.get()
        self.config.start_with_windows = should_autostart
        set_autostart(should_autostart)

        self.config.save()

        if self.on_save:
            self.on_save(self.config)

        self._on_close()

    def _handle_test(self):
        self.config.character = self.selected_char
        self.config.idle_timeout_seconds = self.timeout_var.get()
        self.config.movement_speed = self.speed_var.get()
        self.config.move_physical_cursor = self.move_cursor_var.get()
        self.config.hide_default_cursor = self.hide_cursor_var.get()
        self.config.keep_screen_awake = self.keep_awake_var.get()
        self.config.show_particles = self.particles_var.get()
        self.config.sound_enabled = self.sound_var.get()
        self.config.pause_during_media = self.pause_media_var.get()
        self.config.pause_on_fullscreen = self.pause_fullscreen_var.get()

        should_autostart = self.autostart_var.get()
        self.config.start_with_windows = should_autostart
        set_autostart(should_autostart)

        self.config.save()

        if self.on_save:
            self.on_save(self.config)

        if self.on_test:
            self.on_test()

        self._on_close()

    def _on_close(self):
        self._is_preview_running = False
        if self.window:
            self.window.destroy()
            self.window = None
