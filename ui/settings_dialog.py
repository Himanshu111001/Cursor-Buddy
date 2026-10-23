"""
Modern dark-themed Settings & Customization Dialog for Animated Cursor Buddy.
Includes live preview canvas, sliders, character cards, and behavior toggles.
"""

import time
import tkinter as tk
from tkinter import ttk
from characters import CHARACTERS, get_character
from config import BuddyConfig


class SettingsDialog:
    BG_DARK = "#181926"
    BG_CARD = "#24273A"
    BG_INPUT = "#363A4F"
    TEXT_MAIN = "#CAD3F5"
    TEXT_MUTED = "#8087A2"
    ACCENT = "#8AADF4"
    ACCENT_HOVER = "#7DC4E4"
    SUCCESS = "#A6DA95"

    def __init__(self, parent: tk.Tk, config: BuddyConfig, on_save_callback, on_test_callback):
        self.parent = parent
        self.config = config
        self.on_save = on_save_callback
        self.on_test = on_test_callback
        self.window: tk.Toplevel | None = None
        self.preview_character = get_character(self.config.character)
        self.preview_time = 0.0
        self._is_preview_running = False

    def show(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Animated Cursor Buddy - Settings")
        self.window.geometry("540x660")
        self.window.resizable(False, False)
        self.window.configure(bg=self.BG_DARK)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Center on primary monitor
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x = (sw - 540) // 2
        y = (sh - 660) // 2
        self.window.geometry(f"+{x}+{y}")

        self._build_ui()
        self._is_preview_running = True
        self._run_preview_loop()

    def _build_ui(self):
        # Header banner
        header = tk.Frame(self.window, bg=self.BG_DARK)
        header.pack(fill="x", padx=20, pady=(15, 10))

        title = tk.Label(
            header,
            text="✨ Cursor Buddy Settings",
            font=("Segoe UI", 16, "bold"),
            fg=self.TEXT_MAIN,
            bg=self.BG_DARK,
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Your animated desktop companion that comes to life when you step away.",
            font=("Segoe UI", 9),
            fg=self.TEXT_MUTED,
            bg=self.BG_DARK,
        )
        subtitle.pack(anchor="w")

        # Live Character Preview Frame
        preview_frame = tk.Frame(self.window, bg=self.BG_CARD, highlightthickness=1, highlightbackground=self.BG_INPUT)
        preview_frame.pack(fill="x", padx=20, pady=8)

        self.preview_canvas = tk.Canvas(
            preview_frame,
            width=500,
            height=120,
            bg="#11121D",
            highlightthickness=0,
        )
        self.preview_canvas.pack(pady=10)

        # Character Selector
        char_frame = tk.Frame(self.window, bg=self.BG_DARK)
        char_frame.pack(fill="x", padx=20, pady=6)

        tk.Label(char_frame, text="Companion Character:", font=("Segoe UI", 10, "bold"), fg=self.TEXT_MAIN, bg=self.BG_DARK).pack(anchor="w")

        self.char_var = tk.StringVar(value=self.config.character)
        char_options = [
            ("robot", "🤖 Sparky (Cyber Bot)"),
            ("ghost", "👻 Mochi (Squishy Ghost)"),
            ("cat", "🐱 Neko (Desktop Kitten)"),
            ("fairy", "🧚 Fairy (Starlight Aura)"),
        ]

        char_grid = tk.Frame(char_frame, bg=self.BG_DARK)
        char_grid.pack(fill="x", pady=4)

        for i, (key, label) in enumerate(char_options):
            rb = tk.Radiobutton(
                char_grid,
                text=label,
                value=key,
                variable=self.char_var,
                font=("Segoe UI", 9),
                fg=self.TEXT_MAIN,
                bg=self.BG_DARK,
                activebackground=self.BG_DARK,
                activeforeground=self.ACCENT,
                selectcolor=self.BG_CARD,
                command=self._on_char_change,
            )
            rb.grid(row=i // 2, column=i % 2, sticky="w", padx=10, pady=2)

        # Idle Timeout & Speed Controls
        controls_card = tk.Frame(self.window, bg=self.BG_CARD, highlightthickness=1, highlightbackground=self.BG_INPUT)
        controls_card.pack(fill="x", padx=20, pady=8)

        # Idle timeout slider
        tk.Label(
            controls_card,
            text="Idle Activation Delay (Seconds):",
            font=("Segoe UI", 9, "bold"),
            fg=self.TEXT_MAIN,
            bg=self.BG_CARD,
        ).pack(anchor="w", padx=15, pady=(8, 2))

        slider_row = tk.Frame(controls_card, bg=self.BG_CARD)
        slider_row.pack(fill="x", padx=15, pady=2)

        self.timeout_var = tk.IntVar(value=self.config.idle_timeout_seconds)
        self.timeout_slider = tk.Scale(
            slider_row,
            from_=3,
            to=120,
            orient="horizontal",
            variable=self.timeout_var,
            bg=self.BG_CARD,
            fg=self.TEXT_MAIN,
            highlightthickness=0,
            troughcolor=self.BG_INPUT,
            activebackground=self.ACCENT,
            command=lambda v: self.timeout_label.config(text=f"{v}s"),
        )
        self.timeout_slider.pack(side="left", fill="x", expand=True)

        self.timeout_label = tk.Label(
            slider_row,
            text=f"{self.timeout_var.get()}s",
            font=("Segoe UI", 10, "bold"),
            fg=self.ACCENT,
            bg=self.BG_CARD,
            width=5,
        )
        self.timeout_label.pack(side="right", padx=5)

        # Movement Speed
        speed_row = tk.Frame(controls_card, bg=self.BG_CARD)
        speed_row.pack(fill="x", padx=15, pady=6)

        tk.Label(
            speed_row,
            text="Movement Speed:  ",
            font=("Segoe UI", 9, "bold"),
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
                font=("Segoe UI", 9),
                fg=self.TEXT_MAIN,
                bg=self.BG_CARD,
                activebackground=self.BG_CARD,
                activeforeground=self.ACCENT,
                selectcolor=self.BG_INPUT,
            ).pack(side="left", padx=8)

        # Behavioral Checkboxes
        toggles_card = tk.Frame(self.window, bg=self.BG_CARD, highlightthickness=1, highlightbackground=self.BG_INPUT)
        toggles_card.pack(fill="x", padx=20, pady=8)

        self.move_cursor_var = tk.BooleanVar(value=self.config.move_physical_cursor)
        self.keep_awake_var = tk.BooleanVar(value=self.config.keep_screen_awake)
        self.particles_var = tk.BooleanVar(value=self.config.show_particles)
        self.reactions_var = tk.BooleanVar(value=self.config.show_reactions)

        for text, var in [
            ("Guide physical mouse cursor across desktop", self.move_cursor_var),
            ("Keep screen awake while buddy is active (Prevent Sleep)", self.keep_awake_var),
            ("Show particle effects (Thruster sparks, stardust, bubbles)", self.particles_var),
            ("Show playful reaction emotes (?, zzz, !)", self.reactions_var),
        ]:
            tk.Checkbutton(
                toggles_card,
                text=text,
                variable=var,
                font=("Segoe UI", 9),
                fg=self.TEXT_MAIN,
                bg=self.BG_CARD,
                activebackground=self.BG_CARD,
                activeforeground=self.ACCENT,
                selectcolor=self.BG_INPUT,
            ).pack(anchor="w", padx=15, pady=3)

        # Bottom Action Buttons
        btn_row = tk.Frame(self.window, bg=self.BG_DARK)
        btn_row.pack(fill="x", padx=20, pady=(15, 10))

        test_btn = tk.Button(
            btn_row,
            text="🚀 Test Buddy Now",
            font=("Segoe UI", 10, "bold"),
            bg="#363A4F",
            fg="#F4B8E4",
            activebackground="#494D64",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._handle_test,
        )
        test_btn.pack(side="left")

        save_btn = tk.Button(
            btn_row,
            text="✓ Save & Apply",
            font=("Segoe UI", 10, "bold"),
            bg="#8AADF4",
            fg="#181926",
            activebackground=self.ACCENT_HOVER,
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._handle_save,
        )
        save_btn.pack(side="right")

    def _on_char_change(self):
        new_char_key = self.char_var.get()
        self.preview_character = get_character(new_char_key)

    def _run_preview_loop(self):
        if not self._is_preview_running or not self.window or not self.window.winfo_exists():
            return

        self.preview_time += 0.033
        self.preview_canvas.delete("all")

        # Draw a subtle grid background
        for x in range(0, 500, 25):
            self.preview_canvas.create_line(x, 0, x, 120, fill="#181926", width=1)
        for y in range(0, 120, 25):
            self.preview_canvas.create_line(0, y, 500, y, fill="#181926", width=1)

        # Draw character in center of preview
        self.preview_character.draw(
            canvas=self.preview_canvas,
            cx=250,
            cy=60,
            state="wandering",
            facing_right=True,
            time_sec=self.preview_time,
            scale=1.3,
            particles=None,
        )

        self.window.after(33, self._run_preview_loop)

    def _handle_save(self):
        self.config.character = self.char_var.get()
        self.config.idle_timeout_seconds = self.timeout_var.get()
        self.config.movement_speed = self.speed_var.get()
        self.config.move_physical_cursor = self.move_cursor_var.get()
        self.config.keep_screen_awake = self.keep_awake_var.get()
        self.config.show_particles = self.particles_var.get()
        self.config.show_reactions = self.reactions_var.get()
        self.config.save()

        if self.on_save:
            self.on_save(self.config)

        self._on_close()

    def _handle_test(self):
        # Save first then trigger immediate wake test
        self._handle_save()
        if self.on_test:
            self.on_test()

    def _on_close(self):
        self._is_preview_running = False
        if self.window:
            self.window.destroy()
            self.window = None
