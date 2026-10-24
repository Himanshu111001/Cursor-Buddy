"""
Modern, spacious, industry-level Settings & Customization Dialog for Animated Cursor Buddy.
Engineered with Fluent / macOS design standards: fully responsive, resize-friendly,
smooth mousewheel scrolling, dynamic layout re-flow, and Windows 11 DWM immersive theming.
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
    ModernButton,
    ModernSlider,
    SegmentedPill,
    SpaciousToggleRow,
    apply_dwm_dark_theme,
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
        self.preview_w = 680
        self.preview_h = 78

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

        # Spacious, industry-standard window dimensions
        win_w, win_h = 760, 750
        self.window.geometry(f"{win_w}x{win_h}")
        self.window.minsize(640, 560)
        self.window.resizable(True, True)  # Fully responsive & resize-friendly
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
        # 1. Header Bar (Top)
        header = tk.Frame(self.window, bg=PALETTE["bg_window"])
        header.pack(fill="x", padx=24, pady=(14, 8))

        # Pack shortcut badge on the right FIRST so it is guaranteed full width
        badge_frame = tk.Frame(
            header,
            bg=PALETTE["bg_card_inner"],
            highlightbackground=PALETTE["border"],
            highlightthickness=1,
            padx=12,
            pady=6,
        )
        badge_frame.pack(side="right")

        tk.Label(
            badge_frame,
            text="⚡ Shortcut: Ctrl + Alt + B",
            font=("Segoe UI", 9, "bold"),
            fg=PALETTE["accent_glow"],
            bg=PALETTE["bg_card_inner"],
        ).pack()

        # Title column on the left
        title_col = tk.Frame(header, bg=PALETTE["bg_window"])
        title_col.pack(side="left", fill="x", expand=True)

        title_row = tk.Frame(title_col, bg=PALETTE["bg_window"])
        title_row.pack(anchor="w")

        tk.Label(
            title_row,
            text="✨ Cursor Buddy",
            font=("Segoe UI", 14, "bold"),
            fg=PALETTE["text_main"],
            bg=PALETTE["bg_window"],
        ).pack(side="left")

        tk.Label(
            title_row,
            text=" Control Center",
            font=("Segoe UI", 14, "normal"),
            fg=PALETTE["text_muted"],
            bg=PALETTE["bg_window"],
        ).pack(side="left")

        tk.Label(
            title_col,
            text="Customize your playful companion & autonomous wandering behavior",
            font=("Segoe UI", 8, "normal"),
            fg=PALETTE["text_dim"],
            bg=PALETTE["bg_window"],
        ).pack(anchor="w", pady=(1, 0))

        # 2. Pinned Action Footer (Bottom) - Always visible regardless of window height!
        btn_bar = tk.Frame(
            self.window,
            bg=PALETTE["bg_window"],
            highlightbackground=PALETTE["border"],
            highlightthickness=1,
            padx=24,
            pady=12,
        )
        btn_bar.pack(side="bottom", fill="x")

        ModernButton(
            btn_bar,
            text="🚀 Summon Now",
            command=self._handle_test,
            width=160,
            height=38,
            is_primary=False,
        ).pack(side="left")

        ModernButton(
            btn_bar,
            text="✓ Save & Apply",
            command=self._handle_save,
            width=170,
            height=38,
            is_primary=True,
        ).pack(side="right")

        # 3. Responsive Scrollable Viewport (Middle)
        scroll_container = tk.Frame(self.window, bg=PALETTE["bg_window"])
        scroll_container.pack(fill="both", expand=True)

        self.canvas_scroll = tk.Canvas(
            scroll_container,
            bg=PALETTE["bg_window"],
            highlightthickness=0,
            bd=0,
        )
        self.canvas_scroll.pack(side="left", fill="both", expand=True)

        self.scroll_frame = tk.Frame(self.canvas_scroll, bg=PALETTE["bg_window"])
        self.scroll_window_id = self.canvas_scroll.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw"
        )

        # Make the scroll_frame dynamically span the full canvas width
        self.canvas_scroll.bind(
            "<Configure>",
            lambda e: self.canvas_scroll.itemconfig(self.scroll_window_id, width=e.width),
        )
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all")),
        )

        # 4. Content inside Scroll Frame
        content = tk.Frame(self.scroll_frame, bg=PALETTE["bg_window"])
        content.pack(fill="both", expand=True, padx=24, pady=(2, 12))

        # Section A: Live Character Preview Stage
        preview_container = tk.Frame(
            content,
            bg=PALETTE["bg_card"],
            highlightbackground=PALETTE["border"],
            highlightthickness=1,
        )
        preview_container.pack(fill="x", pady=(0, 10))

        self.preview_canvas = tk.Canvas(
            preview_container,
            height=78,
            bg="#0E1019",
            highlightthickness=0,
            bd=0,
        )
        self.preview_canvas.pack(fill="both", expand=True)
        self.preview_canvas.bind("<Configure>", self._on_preview_configure)

        # Section B: Choose Companion Grid
        tk.Label(
            content,
            text="CHOOSE COMPANION",
            font=("Segoe UI", 8, "bold"),
            fg=PALETTE["text_dim"],
            bg=PALETTE["bg_window"],
        ).pack(anchor="w", pady=(0, 4))

        grid = tk.Frame(content, bg=PALETTE["bg_window"])
        grid.pack(fill="x", pady=(0, 10))
        for col_idx in range(4):
            grid.columnconfigure(col_idx, weight=1)

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
                height=74,
            )
            card.grid(row=0, column=i, sticky="nsew", padx=4)
            self.char_cards[key] = card

        # Section C: Motion & Behavior Card (Side-by-Side: Delay & Speed)
        behavior_card = tk.Frame(
            content,
            bg=PALETTE["bg_card"],
            highlightbackground=PALETTE["border"],
            highlightthickness=1,
            padx=16,
            pady=10,
        )
        behavior_card.pack(fill="x", pady=(0, 10))
        behavior_card.columnconfigure(0, weight=1)
        behavior_card.columnconfigure(1, weight=1)

        # Left Column: Idle Activation Delay
        col_delay = tk.Frame(behavior_card, bg=PALETTE["bg_card"])
        col_delay.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        slider_header = tk.Frame(col_delay, bg=PALETTE["bg_card"])
        slider_header.pack(fill="x")

        tk.Label(
            slider_header,
            text="Idle Activation Delay",
            font=("Segoe UI", 9, "bold"),
            fg=PALETTE["text_main"],
            bg=PALETTE["bg_card"],
        ).pack(side="left")

        self.timeout_var = tk.IntVar(value=self.config.idle_timeout_seconds)
        self.timeout_badge = tk.Label(
            slider_header,
            text=f"{self.timeout_var.get()}s",
            font=("Segoe UI", 9, "bold"),
            fg=PALETTE["accent_glow"],
            bg=PALETTE["bg_card_inner"],
            padx=8,
            pady=1,
        )
        self.timeout_badge.pack(side="right")

        tk.Label(
            col_delay,
            text="Wait time before companion appears",
            font=("Segoe UI", 7, "normal"),
            fg=PALETTE["text_muted"],
            bg=PALETTE["bg_card"],
        ).pack(anchor="w", pady=(1, 4))

        self.timeout_slider = ModernSlider(
            col_delay,
            variable=self.timeout_var,
            from_=3,
            to=60,
            command=lambda v: self.timeout_badge.config(text=f"{v}s"),
            bg=PALETTE["bg_card"],
            accent=PALETTE["accent"],
        )
        self.timeout_slider.pack(fill="x")

        # Right Column: Wander Speed Segmented Control
        col_speed = tk.Frame(behavior_card, bg=PALETTE["bg_card"])
        col_speed.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        speed_header = tk.Frame(col_speed, bg=PALETTE["bg_card"])
        speed_header.pack(fill="x")

        tk.Label(
            speed_header,
            text="Wander Speed",
            font=("Segoe UI", 9, "bold"),
            fg=PALETTE["text_main"],
            bg=PALETTE["bg_card"],
        ).pack(side="left")

        tk.Label(
            col_speed,
            text="Roaming velocity across desktop",
            font=("Segoe UI", 7, "normal"),
            fg=PALETTE["text_muted"],
            bg=PALETTE["bg_card"],
        ).pack(anchor="w", pady=(1, 4))

        self.speed_var = tk.StringVar(value=self.config.movement_speed)
        speed_options = [
            ("slow", "Slow", "🐢"),
            ("normal", "Normal", "⚡"),
            ("fast", "Fast", "🚀"),
        ]
        self.speed_segmented = SegmentedPill(
            col_speed,
            variable=self.speed_var,
            options=speed_options,
            bg=PALETTE["bg_card"],
        )
        self.speed_segmented.pack(fill="x")

        # Section D: Features & Preferences (Spacious Two-Column Grid)
        toggles_container = tk.Frame(content, bg=PALETTE["bg_window"])
        toggles_container.pack(fill="x")
        toggles_container.columnconfigure(0, weight=1)
        toggles_container.columnconfigure(1, weight=1)

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
            padx=6,
            pady=6,
        )
        col1_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        tk.Label(
            col1_card,
            text="POINTER & DISPLAY",
            font=("Segoe UI", 8, "bold"),
            fg=PALETTE["text_dim"],
            bg=PALETTE["bg_card"],
        ).pack(anchor="w", padx=8, pady=(2, 4))

        SpaciousToggleRow(
            col1_card,
            icon="🖱️",
            title="Guide Cursor",
            subtitle="Trigger interactive native UI hovers",
            variable=self.move_cursor_var,
        ).pack(fill="x", pady=1)

        SpaciousToggleRow(
            col1_card,
            icon="👁️",
            title="Hide Native Pointer",
            subtitle="Suppress default system arrow during roam",
            variable=self.hide_cursor_var,
        ).pack(fill="x", pady=1)

        SpaciousToggleRow(
            col1_card,
            icon="☕",
            title="Keep Screen Awake",
            subtitle="Prevent display sleep while active",
            variable=self.keep_awake_var,
        ).pack(fill="x", pady=1)

        SpaciousToggleRow(
            col1_card,
            icon="✨",
            title="Particle FX",
            subtitle="Sparks, stardust aura & emotion bubbles",
            variable=self.particles_var,
        ).pack(fill="x", pady=1)

        # Column 2: System & Detection Card
        col2_card = tk.Frame(
            toggles_container,
            bg=PALETTE["bg_card"],
            highlightbackground=PALETTE["border"],
            highlightthickness=1,
            padx=6,
            pady=6,
        )
        col2_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        tk.Label(
            col2_card,
            text="SMART DETECTION & AUDIO",
            font=("Segoe UI", 8, "bold"),
            fg=PALETTE["text_dim"],
            bg=PALETTE["bg_card"],
        ).pack(anchor="w", padx=8, pady=(2, 4))

        SpaciousToggleRow(
            col2_card,
            icon="🎬",
            title="Pause on Media",
            subtitle="Suppress companion while audio/video plays",
            variable=self.pause_media_var,
        ).pack(fill="x", pady=1)

        SpaciousToggleRow(
            col2_card,
            icon="🎮",
            title="Pause in Fullscreen",
            subtitle="Stay hidden during games and presentations",
            variable=self.pause_fullscreen_var,
        ).pack(fill="x", pady=1)

        SpaciousToggleRow(
            col2_card,
            icon="🔔",
            title="Audio Chimes",
            subtitle="Pleasant procedural retro synth sounds",
            variable=self.sound_var,
        ).pack(fill="x", pady=1)

        SpaciousToggleRow(
            col2_card,
            icon="🚀",
            title="Start with Windows",
            subtitle="Automatically launch in system tray at login",
            variable=self.autostart_var,
        ).pack(fill="x", pady=1)

        # Recursive mousewheel binding so mousewheel works over all cards & elements
        self._bind_mousewheel_recursive(self.scroll_frame)

    def _bind_mousewheel_recursive(self, widget: tk.Widget):
        def _on_wheel(event):
            if "!modernslider" in str(event.widget).lower():
                return
            self.canvas_scroll.yview_scroll(int(-1 * (event.delta / 120)), "units")

        widget.bind("<MouseWheel>", _on_wheel, add="+")
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child)

    def _on_preview_configure(self, event):
        if event.width > 20:
            self.preview_w = event.width
            self.preview_h = event.height

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

        w = self.preview_w
        h = self.preview_h
        cx = w / 2.0
        cy = h / 2.0 + 2

        # Multi-layer ambient radial spotlight
        self.preview_canvas.create_oval(
            cx - 90, cy - 35, cx + 90, cy + 35, fill="#131627", outline=""
        )
        self.preview_canvas.create_oval(
            cx - 55, cy - 20, cx + 55, cy + 20, fill="#1B2038", outline=""
        )

        # Modern cyber grid dots
        for gx in range(32, int(w), 32):
            for gy in range(14, int(h), 22):
                self.preview_canvas.create_oval(gx - 1, gy - 1, gx + 1, gy + 1, fill="#171A29", outline="")

        # LIVE PREVIEW Badge in top right
        self.preview_canvas.create_oval(w - 116, 12, w - 110, 18, fill=PALETTE["accent_cyan"], outline="")
        self.preview_canvas.create_text(
            w - 60,
            15,
            text="LIVE PREVIEW",
            font=("Segoe UI", 8, "bold"),
            fill=PALETTE["text_dim"],
        )

        # Render preview character centered with dynamic scale
        self.preview_character.draw(
            canvas=self.preview_canvas,
            cx=cx,
            cy=cy,
            state="wandering",
            facing_right=True,
            time_sec=self.preview_time,
            scale=1.05,
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
