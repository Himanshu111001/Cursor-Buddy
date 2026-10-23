# Animated Cursor Buddy 🖱️✨

> A lightweight, delightful desktop companion that brings your Windows screen to life when you step away, and instantly disappears the moment you touch your mouse or keyboard!

---

## 🌟 Overview & Highlights

**Animated Cursor Buddy** is a native Windows desktop companion designed to make your workspace feel alive. 
- While you are working, your mouse cursor operates completely as normal.
- Whenever you pause or step away for a configurable idle timeout (e.g., 10 seconds), your choice of an animated companion awakens right at your cursor's last coordinates.
- The companion autonomously explores your desktop, plays with boundary walls, peeks around corners, takes catnaps with floating "Zzz" bubbles, and emits playful particle effects.
- Crucially, it prevents Windows from turning off your display while active using native Windows power management APIs.
- The moment you nudge the mouse or press any key, the companion vanishes without a trace, immediately returning full control to you with zero lag.

---

## 🛠️ Recommended Technology Stack

For **Windows 10/11**, the optimal technology stack is **Python 3.10+ with Native Win32 APIs and a Transparent Layered Tkinter Window**:

| Feature Area | Technology / API | Why It's the Best Choice |
| :--- | :--- | :--- |
| **Idle Detection** | `user32.dll!GetLastInputInfo` | Queries Windows kernel input timestamps directly. Detects physical hardware activity with millisecond accuracy without intrusive keylogging or hook overhead. |
| **Power Management** | `kernel32.dll!SetThreadExecutionState` | Uses official Windows power flags (`ES_CONTINUOUS \| ES_DISPLAY_REQUIRED \| ES_SYSTEM_REQUIRED`) to keep the display awake cleanly without generating artificial input events. |
| **Overlay Window** | Win32 Layered Window (`WS_EX_TRANSPARENT \| WS_EX_LAYERED \| WS_EX_TOOLWINDOW \| WS_EX_NOACTIVATE`) | True 100% click-through transparency. Mouse clicks pass straight through to whatever application or game is below. Won't steal window focus or clutter Alt-Tab. |
| **Graphics & Animation** | Vector Tkinter Canvas + Double Buffering | Zero Chromium / Electron bloat (~15-25 MB RAM vs ~200+ MB for Electron). Crisp vector rendering at 60 FPS across high-DPI displays. |
| **System Tray** | `pystray` + `Pillow` | Native Windows notification tray icon with live status indicators, instant summon button, pause/resume, and settings access. |

---

## 🎭 The Companions

The project comes with **4 built-in procedural animated companions**:

1. **🤖 Sparky the Cyber Bot**: Futuristic floating robot with an animated visor, glowing cyan LED eyes that blink, an antenna alert light, dual flame thrusters, and hovering bob physics.
2. **👻 Mochi the Ghost**: Adorable squishy spirit with wavy floating skirts, squash-and-stretch body deformation, kawaii anime eyes, and blush cheeks.
3. **🐱 Neko the Desktop Cat**: Playful ginger kitten with animated trotting paws, a swishing tail, perky ears, cute whiskers, and napping animations with "Zzz" bubbles.
4. **🧚 Starlight Fairy**: Mystical fairy with fluttering gossamer wings, an iridescent glowing aura, and sparkling star trails that weave across the display.

---

## 🚀 Quick Setup & Usage

### 1. Requirements
Ensure Python 3.10+ is installed on your Windows machine. Standard packages required:
```bash
pip install -r requirements.txt
```
*(Dependencies: `pywin32`, `pystray`, `pillow`)*

### 2. Launching the Companion
Double-click `run.bat` or run from PowerShell / Command Prompt:
```bash
# Normal background mode (watches for idle)
python main.py

# Launch directly with the Settings & Customization dialog open
python main.py --settings

# Instant Test Mode (summons the companion right away without waiting)
python main.py --test
```

---

## ⚙️ Customization & Controls

Access the **Settings Dialog** by right-clicking the system tray icon and selecting **Settings...**, or passing `--settings` on startup:

- **Character Selection**: Choose between Sparky, Mochi, Neko, or Starlight Fairy with a **Live Preview Window**.
- **Idle Timeout**: Configure the inactivity trigger delay (3s to 120s).
- **Movement Speed**: Slow (chill wander), Normal (balanced), or Fast (energetic dashes).
- **Physical Cursor Control**: Toggle whether the companion actively guides the real Windows mouse pointer or roams independently.
- **Power Management**: Toggle whether the display stays awake while the companion is active.
- **Particles & Reactions**: Enable/disable thruster sparks, stardust, curiosity marks (`?`), and sleep bubbles (`zzz`).

### System Tray Quick Actions
Right-click the cursor buddy icon in the Windows taskbar tray:
- **🚀 Summon Buddy Now**: Wake the companion immediately.
- **⏸ Pause / ▶ Resume Buddy**: Temporarily disable without quitting.
- **⚙ Settings...**: Open the full customization dialog.
- **❌ Exit**: Cleanly close the application and restore normal system power states.

---

## 📁 Architecture & File Layout

```
calm-hubble/
├── main.py                     # Main coordinator, state machine & 60 FPS loop
├── config.py                   # Persistent settings manager (config.json)
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows 1-click launcher
├── run.ps1                     # PowerShell launcher
├── system/
│   ├── idle_detector.py        # Win32 GetLastInputInfo idle detection
│   └── power_manager.py        # Win32 SetThreadExecutionState keep-awake
├── engine/
│   ├── movement.py             # Organic AI steering, waypoints, bounce & curiosity
│   ├── overlay_window.py       # Win32 layered click-through canvas window
│   └── particles.py            # Spark, stardust, and sleep bubble particle system
├── characters/
│   ├── base_character.py       # Abstract base character interface
│   ├── robot.py                # 🤖 Sparky the Cyber Bot
│   ├── ghost.py                # 👻 Mochi the Ghost
│   ├── cat.py                  # 🐱 Neko the Desktop Cat
│   └── fairy.py                # 🧚 Starlight Fairy
└── ui/
    ├── settings_dialog.py      # Modern dark-theme GUI with live character preview
    └── tray.py                 # System tray controller with status icon
```

---

## 🛡️ License
Released under the MIT License. Feel free to extend with new characters and behaviors!
