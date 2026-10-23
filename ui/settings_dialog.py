"""
Modern, sleek, compact Settings & Customization Dialog for Animated Cursor Buddy.
Engineered to fit comfortably within all screen resolutions (including 720p/1080p with scaling).
"""

import os
import tkinter as tk
from tkinter import ttk
from characters import CHARACTERS, get_character
from config import BuddyConfig
from system import get_desktop_work_area, is_autostart_enabled, set_autostart


class SettingsDialog:
    # Palette: Modern Catppuccin Macchiato Dark
    BG_DARK = "#1E1F29"
    BG_CARD = "#282A36"
    BG_HOVER = "#343746"
    BG_ACTIVE = "#44475A"
    TEXT_MAIN = "#F8F8F2"
    TEXT_MUTED = "#9DA5B4"
    ACCENT = "#8BE9FD"
    ACCENT_PURPLE = "#BD93F9"
    ACCENT_GREEN = "#50FA7B"
    ACCENT_PINK = "#FF79C6"

    def __init__(self, parent: tk.Tk, config: BuddyConfig, on_save_callback, on_test_callback):
        self.parent = parent
        self.config = config
        self.on_save = on_save_callback
        self.on_test = on_test_callback
        self.window: tk.Toplevel | None = None
        self.preview_character = get_character(self.config.character)
        self.preview_time = 0.0
        self._is_preview_running = False
        self.char_buttons: dict[str, tk.Button] = {}

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

        # Dimensions strictly designed to fit 720p/1080p laptop displays without cutting off
        win_w, win_h = 490, 560
        self.window.geometry(f"{win_w}x{win_h}")
        self.window.resizable(False, False)
        self.window.configure(bg=self.BG_DARK)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Center inside usable desktop work area (above taskbar)
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

        self._build_ui()
        self._is_preview_running = True
        self._run_preview_loop()

    def _build_ui(self):
        # 1. Header Row
        header = tk.Frame(self.window, bg=self.BG_DARK)
        header.pack(fill="x", padx=16, pady=(10, 4))

        title_row = tk.Frame(header, bg=self.BG_DARK)
        title_row.pack(fill="x")

        tk.Label(
            title_row,
            text="✨ Cursor Buddy Control Center",
            font=("Segoe UI", 13, "bold"),
            fg=self.TEXT_MAIN,
            bg=self.BG_DARK,
        ).pack(side="left")

        tk.Label(
            title_row,
            text="Ctrl+Alt+B to summon",
            font=("Segoe UI", 8, "bold"),
            fg=self.ACCENT_PURPLE,
            bg=self.BG_CARD,
            padx=6,
            pady=2,
        ).pack(side="right")

        # 2. Live Character Preview Card
        preview_card = tk.Frame(self.window, bg=self.BG_CARD, bd=1, relief="solid")
        preview_card.pack(fill="x", padx=16, pady=4)

        self.preview_canvas = tk.Canvas(
            preview_card,
            width=450,
            height=85,
            bg="#16171E",
            highlightthickness=0,
            bd=0,
        )
        self.preview_canvas.pack(pady=4)

        # 3. Character Selector Grid (Clickable cards)
        char_box = tk.Frame(self.window, bg=self.BG_DARK)
        char_box.pack(fill="x", padx=16, pady=4)

        tk.Label(
            char_box,
            text="Choose Companion:",
            font=("Segoe UI", 9, "bold"),
            fg=self.TEXT_MAIN,
            bg=self.BG_DARK,
        ).pack(anchor="w", pady=(0, 2))

        grid = tk.Frame(char_box, bg=self.BG_DARK)
        grid.pack(fill="x")

        self.selected_char = self.config.character
        char_options = [
            ("robot", "🤖 Sparky", "Cyber Bot"),
            ("ghost", "👻 Mochi", "Squishy Ghost"),
            ("cat", "🐱 Neko", "Playful Kitten"),
            ("fairy", "🧚 Fairy", "Starlight Aura"),
        ]

        self.char_buttons = {}
        for i, (key, label, desc) in enumerate(char_options):
            col = i % 4
            btn = tk.Button(
                grid,
                text=f"{label}\n{desc}",
                font=("Segoe UI", 8),
                bg=self.ACCENT_PURPLE if key == self.selected_char else self.BG_CARD,
                fg="#1E1F29" if key == self.selected_char else self.TEXT_MAIN,
                activebackground=self.BG_ACTIVE,
                activeforeground=self.TEXT_MAIN,
                relief="flat",
                bd=0,
                padx=4,
                pady=6,
                cursor="hand2",
                command=lambda k=key: self._select_char(k),
            )
            btn.grid(row=0, column=col, sticky="ew", padx=3, pady=2)
            grid.columnconfigure(col, weight=1)
            self.char_buttons[key] = btn

        # 4. Settings Card (Delay, Speed & Toggles)
        settings_card = tk.Frame(self.window, bg=self.BG_CARD)
        settings_card.pack(fill="x", padx=16, pady=6)

        # Delay Slider Row
        slider_row = tk.Frame(settings_card, bg=self.BG_CARD)
        slider_row.pack(fill="x", padx=12, pady=(6, 2))

        tk.Label(
            slider_row,
            text="Idle Activation Delay: ",
            font=("Segoe UI", 8, "bold"),
            fg=self.TEXT_MAIN,
            bg=self.BG_CARD,
        ).pack(side="left")

        self.timeout_var = tk.IntVar(value=self.config.idle_timeout_seconds)
        self.timeout_label = tk.Label(
            slider_row,
            text=f"{self.timeout_var.get()}s",
            font=("Segoe UI", 9, "bold"),
            fg=self.ACCENT,
            bg=self.BG_CARD,
            width=4,
        )
        self.timeout_label.pack(side="right")

        self.timeout_slider = tk.Scale(
            slider_row,
            from_=3,
            to=60,
            orient="horizontal",
            variable=self.timeout_var,
            bg=self.BG_CARD,
            fg=self.TEXT_MAIN,
            highlightthickness=0,
            troughcolor=self.BG_DARK,
            activebackground=self.ACCENT,
            bd=0,
            showvalue=0,
            command=lambda v: self.timeout_label.config(text=f"{v}s"),
        )
        self.timeout_slider.pack(side="left", fill="x", expand=True, padx=6)

        # Speed row
        speed_row = tk.Frame(settings_card, bg=self.BG_CARD)
        speed_row.pack(fill="x", padx=12, pady=2)

        tk.Label(
            speed_row,
            text="Wander Speed: ",
            font=("Segoe UI", 8, "bold"),
            fg=self.TEXT_MAIN,
            bg=self.BG_CARD,
        ).pack(side="left")

        self.speed_var = tk.StringVar(value=self.config.movement_speed)
        for spd in ["slow", "normal", "fast"]:
            tk.Radiobutton(
                speed_row,
                text=spd.capitalize(),
                value=spd,
                variable=self.speed_var,
                font=("Segoe UI", 8),
                fg=self.TEXT_MAIN,
                bg=self.BG_CARD,
                activebackground=self.BG_CARD,
                activeforeground=self.ACCENT,
                selectcolor=self.BG_DARK,
            ).pack(side="left", padx=6)

        # Checkboxes (2 columns for compact layout)
        check_box = tk.Frame(settings_card, bg=self.BG_CARD)
        check_box.pack(fill="x", padx=12, pady=(4, 8))

        self.move_cursor_var = tk.BooleanVar(value=self.config.move_physical_cursor)
        self.hide_cursor_var = tk.BooleanVar(value=self.config.hide_default_cursor)
        self.keep_awake_var = tk.BooleanVar(value=self.config.keep_screen_awake)
        self.particles_var = tk.BooleanVar(value=self.config.show_particles)
        self.sound_var = tk.BooleanVar(value=self.config.sound_enabled)
        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())
        self.pause_media_var = tk.BooleanVar(value=self.config.pause_during_media)
        self.pause_fullscreen_var = tk.BooleanVar(value=self.config.pause_on_fullscreen)

        toggles = [
            ("Guide mouse cursor", self.move_cursor_var),
            ("Hide default mouse pointer", self.hide_cursor_var),
            ("Keep display awake", self.keep_awake_var),
            ("Show particle effects", self.particles_var),
            ("Play wake/sleep chimes", self.sound_var),
            ("Launch on Windows startup", self.autostart_var),
            ("Pause during video/media", self.pause_media_var),
            ("Pause in fullscreen apps", self.pause_fullscreen_var),
        ]

        for i, (text, var) in enumerate(toggles):
            r = i // 2
            c = i % 2
            cb = tk.Checkbutton(
                check_box,
                text=text,
                variable=var,
                font=("Segoe UI", 8),
                fg=self.TEXT_MAIN,
                bg=self.BG_CARD,
                activebackground=self.BG_CARD,
                activeforeground=self.ACCENT,
                selectcolor=self.BG_DARK,
            )
            cb.grid(row=r, column=c, sticky="w", padx=4, pady=1)

        # 5. Bottom Actions Bar (Guaranteed visible)
        btn_bar = tk.Frame(self.window, bg=self.BG_DARK)
        btn_bar.pack(fill="x", padx=16, pady=(6, 8))

        test_btn = tk.Button(
            btn_bar,
            text="🚀 Test Buddy Now",
            font=("Segoe UI", 9, "bold"),
            bg="#44475A",
            fg=self.ACCENT_PINK,
            activebackground="#6272A4",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._handle_test,
        )
        test_btn.pack(side="left")

        save_btn = tk.Button(
            btn_bar,
            text="✓ Save & Apply",
            font=("Segoe UI", 9, "bold"),
            bg=self.ACCENT_GREEN,
            fg="#1E1F29",
            activebackground="#8BE9FD",
            relief="flat",
            bd=0,
            padx=18,
            pady=7,
            cursor="hand2",
            command=self._handle_save,
        )
        save_btn.pack(side="right")

    def _select_char(self, char_key: str):
        self.selected_char = char_key
        self.preview_character = get_character(char_key)
        for k, btn in self.char_buttons.items():
            if k == char_key:
                btn.config(bg=self.ACCENT_PURPLE, fg="#1E1F29")
            else:
                btn.config(bg=self.BG_CARD, fg=self.TEXT_MAIN)

    def _run_preview_loop(self):
        if not self._is_preview_running or not self.window or not self.window.winfo_exists():
            return

        self.preview_time += 0.033
        self.preview_canvas.delete("all")

        # Subtle dark grid
        for x in range(0, 450, 20):
            self.preview_canvas.create_line(x, 0, x, 85, fill="#1E1F29", width=1)
        for y in range(0, 85, 20):
            self.preview_canvas.create_line(0, y, 450, y, fill="#1E1F29", width=1)

        # Render preview character
        self.preview_character.draw(
            canvas=self.preview_canvas,
            cx=225,
            cy=42,
            state="wandering",
            facing_right=True,
            time_sec=self.preview_time,
            scale=1.1,
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
        self._handle_save()
        if self.on_test:
            self.on_test()

    def _on_close(self):
        self._is_preview_running = False
        if self.window:
            self.window.destroy()
            self.window = None
