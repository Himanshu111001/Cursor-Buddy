# Animated Cursor Buddy 🖱️✨

> A lightweight, delightful desktop application that brings your Windows screen to life when you step away, and instantly disappears the moment you touch your mouse or keyboard!

---

## 🌟 What Makes It a Real, Useful Windows App?

**Animated Cursor Buddy** is packaged as a complete, self-contained Windows desktop utility:
- **Standalone Windows Executable**: Bundled with PyInstaller as `AnimatedCursorBuddy.exe`—runs natively without having to open a terminal or command prompt.
- **Desktop & Start Menu Shortcuts**: 1-click installer creates Start Menu and Desktop shortcuts with high-resolution custom icons (`.ico`).
- **Global Hotkey (`Ctrl + Alt + B`)**: Summon or dismiss your companion anytime from any screen or game with a single keyboard shortcut.
- **Windows Startup Integration**: Toggle "Start with Windows on boot" directly from the Settings dialog to keep your companion watching automatically.
- **Screen Awake Protection**: Uses Win32 `SetThreadExecutionState` so your laptop display won't go to sleep while your buddy is wandering.
- **Dual-Sensor Instant Dismiss**: Responds in < 150ms to any physical mouse movement or keystroke, immediately restoring your normal cursor with zero lag.
- **Procedural Sound Chimes**: Optional gentle, playful rising/falling audio chimes when your buddy awakens or rests.

---

## 🎭 The 4 Companion Characters

1. **🤖 Sparky the Cyber Bot**: Futuristic floating robot with an animated visor, glowing cyan LED eyes that blink, an antenna alert beacon, dual flame thrusters, and hovering bob physics.
2. **👻 Mochi the Ghost**: Adorable squishy spirit with wavy floating skirts, squash-and-stretch body deformation, kawaii anime eyes, and blush cheeks.
3. **🐱 Neko the Desktop Cat**: Playful ginger kitten with animated trotting paws, a swishing tail, perky ears, cute whiskers, and napping animations with "Zzz" bubbles.
4. **🧚 Starlight Fairy**: Mystical fairy with fast-fluttering gossamer wings, an iridescent glowing core halo, and sparkling stardust particle trails.

---

## 🚀 How to Run & Use

### Option 1: Double-Click the Desktop Shortcut (Recommended)
An **"Animated Cursor Buddy"** shortcut has already been installed directly to your **Desktop** and **Start Menu**. Just double-click it!

### Option 2: Run the Standalone Compiled Executable
Navigate to:
```
dist\AnimatedCursorBuddy\AnimatedCursorBuddy.exe
```
This is a self-contained, windowed executable with zero terminal popups.

### Option 3: Silent Background Runner
Double-click `CursorBuddy.vbs` to launch silently in the background.

### Option 4: From PowerShell / Command Prompt
```powershell
# Normal idle watch mode
python main.py

# Instant summon (test mode)
python main.py --test

# Open Settings & Live Character Preview dialog
python main.py --settings
```

---

## ⌨️ Shortcuts & Controls

| Action | Control |
| :--- | :--- |
| **Summon / Dismiss Companion** | **`Ctrl + Alt + B`** (Global Hotkey from anywhere) |
| **Instant Interruption** | Move physical mouse or press any key |
| **System Tray Actions** | Right-click tray icon -> *Summon Buddy*, *Pause/Resume*, *Settings*, *Exit* |
| **Customize & Tune** | Open **Settings...** from tray or pass `--settings` |

---

## ⚙️ Customization Settings

Open the **Settings Dialog** to configure:
* **Companion Selector**: Switch between Robot, Ghost, Cat, or Fairy with a **Live Preview Canvas**.
* **Idle Activation Delay**: Slider from 3 seconds up to 120 seconds.
* **Movement Speed**: Slow, Normal, or Fast wandering.
* **Cursor Mode**: Choose whether the companion physically guides your mouse pointer or roams freely.
* **Start with Windows**: Automatically launch on Windows boot.
* **Display Keep-Awake**: Keep your laptop screen illuminated while the companion is active.
* **Particle FX & Reactions**: Toggle thruster sparks, stardust, question marks (`?`), and sleep bubbles (`zzz`).
* **Audio Chimes**: Toggle pleasant procedural synth tones on wake and sleep.

---

## 🔨 Building & Re-bundling

To re-compile the standalone executable or update shortcuts at any time:
```powershell
# 1-Click build standalone EXE
.\build.bat

# Or rebuild via Python
python build_exe.py

# Refresh Desktop and Start Menu shortcuts
python install_shortcuts.py
```

---

## 📁 Project Architecture

```
calm-hubble/
├── dist/AnimatedCursorBuddy/    # Standalone compiled Windows application
├── main.py                      # Core coordinator, state machine & 60 FPS loop
├── config.py                    # Persistent JSON preferences manager
├── CursorBuddy.vbs              # Silent background launcher
├── install_shortcuts.py         # Desktop & Start Menu shortcut installer
├── generate_assets.py           # Multi-resolution app icon generator
├── build_exe.py                 # PyInstaller standalone build pipeline
├── build.bat                    # 1-click executable builder
├── run.bat                      # 1-click Python runner
├── system/
│   ├── idle_detector.py         # Win32 GetLastInputInfo idle detection
│   ├── power_manager.py         # Win32 SetThreadExecutionState display keep-awake
│   ├── autostart.py             # Windows Registry autostart integration
│   ├── hotkey.py                # Global Ctrl+Alt+B keyboard hook
│   └── audio.py                 # Async procedural sound effects
├── engine/
│   ├── movement.py              # Organic AI steering, waypoints, bounce & curiosity
│   ├── overlay_window.py        # Win32 layered click-through canvas window
│   └── particles.py             # Sparks, stardust, reaction bubbles
├── characters/
│   ├── base_character.py        # Abstract character interface
│   ├── robot.py                 # 🤖 Sparky the Cyber Bot
│   ├── ghost.py                 # 👻 Mochi the Ghost
│   ├── cat.py                   # 🐱 Neko the Desktop Cat
│   └── fairy.py                 # 🧚 Starlight Fairy
└── ui/
    ├── settings_dialog.py       # Dark-themed GUI with live preview & autostart
    └── tray.py                  # System tray controller with status icon
```
