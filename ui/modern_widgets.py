"""
Modern, sleek Fluent/macOS-inspired custom Tkinter widgets for Animated Cursor Buddy.
Includes smooth canvas-rendered switches, sliders, segmented pills, character cards,
compact toggle rows, and Windows 11 DWM immersive dark theming.
"""

from __future__ import annotations

import ctypes
import tkinter as tk
from typing import Any, Callable, Sequence


# Ultra-Modern Obsidian & Electric Indigo Palette
PALETTE = {
    "bg_window": "#0C0D14",
    "bg_card": "#131622",
    "bg_card_inner": "#1A1D2E",
    "bg_hover": "#21253B",
    "border": "#222638",
    "border_light": "#323850",
    "accent": "#6366F1",        # Electric Indigo
    "accent_hover": "#4F46E5",
    "accent_glow": "#818CF8",
    "accent_cyan": "#06B6D4",
    "accent_green": "#10B981",
    "text_main": "#F8FAFC",
    "text_muted": "#94A3B8",
    "text_dim": "#64748B",
    "btn_secondary": "#1A1D2C",
    "btn_secondary_border": "#2A3047",
    "btn_secondary_hover": "#252A40",
}


def apply_dwm_dark_theme(window: tk.Toplevel | tk.Tk, bg_color_hex: str = "#0C0D14"):
    """
    Applies Windows 11 / Windows 10 DWM immersive dark mode and caption styling
    so the OS title bar seamlessly integrates with the dark theme.
    """
    try:
        window.update_idletasks()
        hwnd = int(window.wm_frame(), 16)
        if not hwnd:
            hwnd = window.winfo_id()

        dwmapi = ctypes.windll.dwmapi

        # 1. DWMWA_USE_IMMERSIVE_DARK_MODE (20 on Win11/Win10 20H1+, 19 on older Win10)
        true_val = ctypes.c_int(1)
        res = dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(true_val), ctypes.sizeof(true_val))
        if res != 0:
            dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(true_val), ctypes.sizeof(true_val))

        # 2. DWMWA_CAPTION_COLOR (35) - Title bar color (COLORREF: 0x00BBGGRR)
        r = int(bg_color_hex[1:3], 16)
        g = int(bg_color_hex[3:5], 16)
        b = int(bg_color_hex[5:7], 16)
        color_ref = ctypes.c_int((b << 16) | (g << 8) | r)
        dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(color_ref), ctypes.sizeof(color_ref))

        # 3. DWMWA_TEXT_COLOR (36) - Title text
        text_color = ctypes.c_int(0x00F8FAFC)
        dwmapi.DwmSetWindowAttribute(hwnd, 36, ctypes.byref(text_color), ctypes.sizeof(text_color))

        # 4. DWMWA_BORDER_COLOR (34) - Border color
        border_color = ctypes.c_int(0x00382622)
        dwmapi.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(border_color), ctypes.sizeof(border_color))
    except Exception:
        pass


def draw_rounded_rect(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    radius: float,
    fill: str,
    outline: str = "",
    width: int = 1,
    tags: str | tuple[str, ...] = (),
):
    """Draws a clean rounded rectangle on canvas without internal grid lines."""
    r = max(1.0, min(radius, (x2 - x1) / 2.0, (y2 - y1) / 2.0))
    # 1. Solid fill body
    canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, fill=fill, outline="", tags=tags)
    canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, fill=fill, outline="", tags=tags)
    canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, fill=fill, outline="", tags=tags)
    canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, fill=fill, outline="", tags=tags)
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline="", tags=tags)
    canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill, outline="", tags=tags)

    # 2. Perimeter outline if requested
    if outline:
        canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, outline=outline, width=width, style="arc", tags=tags)
        canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, outline=outline, width=width, style="arc", tags=tags)
        canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, outline=outline, width=width, style="arc", tags=tags)
        canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, outline=outline, width=width, style="arc", tags=tags)
        canvas.create_line(x1 + r, y1, x2 - r, y1, fill=outline, width=width, tags=tags)
        canvas.create_line(x2, y1 + r, x2, y2 - r, fill=outline, width=width, tags=tags)
        canvas.create_line(x1 + r, y2, x2 - r, y2, fill=outline, width=width, tags=tags)
        canvas.create_line(x1, y1 + r, x1, y2 - r, fill=outline, width=width, tags=tags)


class ModernSwitch(tk.Canvas):
    """
    Sleek iOS/Fluent pill toggle switch with smooth circular thumb.
    """

    def __init__(
        self,
        parent: tk.Widget,
        variable: tk.BooleanVar,
        command: Callable[[], None] | None = None,
        width: int = 34,
        height: int = 18,
        bg: str = PALETTE["bg_card"],
        accent: str = PALETTE["accent"],
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.var = variable
        self.command = command
        self.w = width
        self.h = height
        self.r = height / 2.0
        self.accent = accent

        self.bind("<Button-1>", self._on_click)
        self.var.trace_add("write", lambda *_: self.render())
        self.render()

    def set_bg(self, bg: str):
        self.configure(bg=bg)

    def render(self):
        self.delete("all")
        is_on = bool(self.var.get())
        if is_on:
            draw_rounded_rect(self, 1, 1, self.w - 1, self.h - 1, self.r - 1, fill=self.accent)
            cx = self.w - self.r
            cy = self.h / 2.0
            tr = self.r - 2.5
            self.create_oval(cx - tr, cy - tr, cx + tr, cy + tr, fill="#FFFFFF", outline="")
        else:
            draw_rounded_rect(
                self,
                1,
                1,
                self.w - 1,
                self.h - 1,
                self.r - 1,
                fill=PALETTE["bg_card_inner"],
                outline=PALETTE["border_light"],
            )
            cx = self.r
            cy = self.h / 2.0
            tr = self.r - 3.5
            self.create_oval(cx - tr, cy - tr, cx + tr, cy + tr, fill=PALETTE["text_dim"], outline="")

    def _on_click(self, event=None):
        self.var.set(not self.var.get())
        if self.command:
            self.command()


class CompactToggleRow(tk.Frame):
    """
    Compact, modern single-line settings row with icon, title, and ModernSwitch.
    Hovering highlights the row; clicking anywhere toggles the switch.
    """

    def __init__(
        self,
        parent: tk.Widget,
        icon: str,
        title: str,
        variable: tk.BooleanVar,
        command: Callable[[], None] | None = None,
        bg: str = PALETTE["bg_card"],
    ):
        super().__init__(parent, bg=bg, cursor="hand2")
        self.variable = variable
        self.command = command
        self.bg_default = bg
        self.bg_hover = PALETTE["bg_hover"]

        # Label: Icon + Title
        self.lbl = tk.Label(
            self,
            text=f"{icon}  {title}",
            font=("Segoe UI", 8, "bold"),
            fg=PALETTE["text_main"],
            bg=bg,
            anchor="w",
        )
        self.lbl.pack(side="left", fill="x", expand=True, padx=(8, 4), pady=4)

        # Switch
        self.switch = ModernSwitch(
            self,
            variable=self.variable,
            command=self._on_toggled,
            bg=bg,
            width=34,
            height=18,
        )
        self.switch.pack(side="right", padx=(4, 8), pady=4)

        for widget in (self, self.lbl):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)

    def _on_enter(self, event=None):
        self.configure(bg=self.bg_hover)
        self.lbl.configure(bg=self.bg_hover)
        self.switch.set_bg(self.bg_hover)

    def _on_leave(self, event=None):
        self.configure(bg=self.bg_default)
        self.lbl.configure(bg=self.bg_default)
        self.switch.set_bg(self.bg_default)

    def _on_click(self, event=None):
        self.variable.set(not self.variable.get())
        self._on_toggled()

    def _on_toggled(self):
        self.switch.render()
        if self.command:
            self.command()


class ModernSlider(tk.Canvas):
    """
    Fluid canvas slider with accent progress fill and circular knob.
    """

    def __init__(
        self,
        parent: tk.Widget,
        variable: tk.IntVar,
        from_: int = 3,
        to: int = 60,
        command: Callable[[int], None] | None = None,
        height: int = 22,
        bg: str = PALETTE["bg_card"],
        accent: str = PALETTE["accent"],
    ):
        super().__init__(
            parent,
            height=height,
            bg=bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.var = variable
        self.from_ = from_
        self.to = to
        self.command = command
        self.w = 200
        self.h = height
        self.padding = 8
        self.accent = accent

        self.bind("<Configure>", self._on_configure)
        self.bind("<Button-1>", self._on_drag)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.var.trace_add("write", lambda *_: self.render())

    def _on_configure(self, event):
        if event.width > 20:
            self.w = event.width
            self.render()

    def _val_to_x(self, val: int) -> float:
        usable = self.w - 2 * self.padding
        ratio = (val - self.from_) / (self.to - self.from_)
        return self.padding + max(0.0, min(1.0, ratio)) * usable

    def _x_to_val(self, x: float) -> int:
        usable = self.w - 2 * self.padding
        clamped_x = max(self.padding, min(self.w - self.padding, x))
        ratio = (clamped_x - self.padding) / usable
        val = self.from_ + ratio * (self.to - self.from_)
        return int(round(val))

    def _on_drag(self, event):
        val = self._x_to_val(event.x)
        self.var.set(val)
        if self.command:
            self.command(val)

    def _on_mousewheel(self, event):
        delta = 1 if event.delta > 0 else -1
        new_val = max(self.from_, min(self.to, self.var.get() + delta))
        self.var.set(new_val)
        if self.command:
            self.command(new_val)

    def render(self):
        self.delete("all")
        cy = self.h / 2.0
        val = self.var.get()
        thumb_x = self._val_to_x(val)

        # Inactive track
        self.create_line(
            self.padding,
            cy,
            self.w - self.padding,
            cy,
            fill=PALETTE["bg_card_inner"],
            width=5,
            capstyle="round",
        )
        # Active progress track
        if thumb_x > self.padding:
            self.create_line(
                self.padding,
                cy,
                thumb_x,
                cy,
                fill=self.accent,
                width=5,
                capstyle="round",
            )
        # Circular knob
        self.create_oval(
            thumb_x - 6.5,
            cy - 6.5,
            thumb_x + 6.5,
            cy + 6.5,
            fill="#FFFFFF",
            outline=PALETTE["accent_hover"],
            width=2,
        )


class SegmentedPill(tk.Frame):
    """
    Modern segmented control / pill bar for options like [Slow | Normal | Fast].
    """

    def __init__(
        self,
        parent: tk.Widget,
        variable: tk.StringVar,
        options: Sequence[tuple[str, str, str]],  # (key, label, emoji)
        command: Callable[[str], None] | None = None,
        bg: str = PALETTE["bg_card"],
    ):
        super().__init__(parent, bg=bg)
        self.variable = variable
        self.options = options
        self.command = command
        self.buttons: dict[str, tk.Label] = {}

        self.container = tk.Frame(self, bg=PALETTE["bg_card_inner"], padx=2, pady=2)
        self.container.pack(fill="x")

        for key, label, emoji in self.options:
            btn = tk.Label(
                self.container,
                text=f"{emoji} {label}",
                font=("Segoe UI", 8, "bold"),
                cursor="hand2",
                padx=8,
                pady=3,
            )
            btn.pack(side="left", fill="x", expand=True, padx=2)
            btn.bind("<Button-1>", lambda e, k=key: self._select(k))
            self.buttons[key] = btn

        self.variable.trace_add("write", lambda *_: self.render())
        self.render()

    def _select(self, key: str):
        self.variable.set(key)
        if self.command:
            self.command(key)

    def render(self):
        curr = self.variable.get()
        for k, btn in self.buttons.items():
            if k == curr:
                btn.configure(
                    bg=PALETTE["accent"],
                    fg="#FFFFFF",
                )
            else:
                btn.configure(
                    bg=PALETTE["bg_card_inner"],
                    fg=PALETTE["text_muted"],
                )


class CompanionCard(tk.Canvas):
    """
    Rich interactive character tile featuring the actual custom-drawn companion avatar,
    name, persona, active glow border, and status badge.
    """

    def __init__(
        self,
        parent: tk.Widget,
        char_key: str,
        name: str,
        persona: str,
        character_instance: Any,
        is_selected: bool,
        on_click: Callable[[str], None],
        width: int = 120,
        height: int = 68,
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=PALETTE["bg_window"],
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.char_key = char_key
        self.name = name
        self.persona = persona
        self.character = character_instance
        self.is_selected = is_selected
        self.on_click = on_click
        self.w = width
        self.h = height
        self.is_hovered = False

        self.bind("<Button-1>", self._handle_click)
        self.bind("<Enter>", self._handle_enter)
        self.bind("<Leave>", self._handle_leave)
        self.render()

    def set_selected(self, selected: bool):
        if self.is_selected != selected:
            self.is_selected = selected
            self.render()

    def _handle_click(self, event=None):
        self.on_click(self.char_key)

    def _handle_enter(self, event=None):
        self.is_hovered = True
        self.render()

    def _handle_leave(self, event=None):
        self.is_hovered = False
        self.render()

    def render(self):
        self.delete("all")
        if self.is_selected:
            bg_color = PALETTE["bg_hover"]
            border_color = PALETTE["accent"]
            border_w = 2
        elif self.is_hovered:
            bg_color = PALETTE["bg_card_inner"]
            border_color = PALETTE["border_light"]
            border_w = 1
        else:
            bg_color = PALETTE["bg_card"]
            border_color = PALETTE["border"]
            border_w = 1

        draw_rounded_rect(
            self,
            1,
            1,
            self.w - 1,
            self.h - 1,
            7,
            fill=bg_color,
            outline=border_color,
            width=border_w,
        )

        # Selected corner indicator
        if self.is_selected:
            self.create_oval(self.w - 12, 5, self.w - 5, 12, fill=PALETTE["accent"], outline="")
            self.create_oval(self.w - 10, 7, self.w - 7, 10, fill="#FFFFFF", outline="")

        # Draw character avatar centered at top
        if self.character:
            try:
                self.character.draw(
                    canvas=self,
                    cx=self.w / 2.0,
                    cy=20,
                    state="idle",
                    facing_right=True,
                    time_sec=0.5,
                    scale=0.5,
                    particles=None,
                )
            except Exception:
                pass

        # Name
        self.create_text(
            self.w / 2.0,
            44,
            text=self.name,
            font=("Segoe UI", 8, "bold"),
            fill="#FFFFFF" if self.is_selected else PALETTE["text_main"],
        )

        # Subtitle / Persona
        self.create_text(
            self.w / 2.0,
            57,
            text=self.persona,
            font=("Segoe UI", 7, "normal"),
            fill=PALETTE["accent_glow"] if self.is_selected else PALETTE["text_muted"],
        )


class ModernButton(tk.Canvas):
    """
    Sleek custom rounded button with hover glow and tactile click.
    """

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command: Callable[[], None],
        width: int = 150,
        height: int = 36,
        is_primary: bool = False,
        bg_parent: str = PALETTE["bg_window"],
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg_parent,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.text = text
        self.command = command
        self.w = width
        self.h = height
        self.is_primary = is_primary
        self.is_hovered = False
        self.is_pressed = False

        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.render()

    def _on_enter(self, event=None):
        self.is_hovered = True
        self.render()

    def _on_leave(self, event=None):
        self.is_hovered = False
        self.is_pressed = False
        self.render()

    def _on_press(self, event=None):
        self.is_pressed = True
        self.render()

    def _on_release(self, event=None):
        if self.is_pressed:
            self.is_pressed = False
            self.render()
            self.command()

    def render(self):
        self.delete("all")
        r = 7
        if self.is_primary:
            if self.is_pressed:
                fill = "#4338CA"
            elif self.is_hovered:
                fill = PALETTE["accent_hover"]
            else:
                fill = PALETTE["accent"]
            outline = ""
            text_color = "#FFFFFF"
        else:
            if self.is_pressed:
                fill = "#141724"
            elif self.is_hovered:
                fill = PALETTE["btn_secondary_hover"]
            else:
                fill = PALETTE["btn_secondary"]
            outline = PALETTE["btn_secondary_border"]
            text_color = PALETTE["accent_glow"] if self.is_hovered else PALETTE["text_main"]

        draw_rounded_rect(self, 1, 1, self.w - 1, self.h - 1, r, fill=fill, outline=outline, width=1)
        self.create_text(
            self.w / 2.0,
            self.h / 2.0,
            text=self.text,
            font=("Segoe UI", 9, "bold"),
            fill=text_color,
        )
