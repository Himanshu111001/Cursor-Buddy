"""
PyInstaller build script to bundle Animated Cursor Buddy into a standalone Windows executable.
"""

import os
import shutil
import subprocess
import sys


def build():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    # 1. Ensure assets are generated
    icon_ico = os.path.join(project_dir, "assets", "icon.ico")
    if not os.path.exists(icon_ico):
        print("[Build] Generating app assets...")
        import generate_assets
        generate_assets.generate_app_icon()

    # 2. PyInstaller arguments
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=AnimatedCursorBuddy",
        f"--icon={icon_ico}",
        f"--add-data=assets;assets",
        f"--add-data=characters;characters",
        f"--add-data=engine;engine",
        f"--add-data=system;system",
        f"--add-data=ui;ui",
        "--hidden-import=pystray",
        "--hidden-import=PIL",
        "--hidden-import=win32gui",
        "--hidden-import=win32api",
        "--hidden-import=win32con",
        "--hidden-import=win32com",
        "--hidden-import=win32process",
        "--clean",
        "main.py",
    ]

    print("[Build] Compiling standalone Windows executable with PyInstaller...")
    print("Command:", " ".join(cmd))
    res = subprocess.run(cmd)

    if res.returncode == 0:
        print("\n=======================================================")
        print(" [SUCCESS] App bundled successfully!")
        print(f" Executable: {os.path.join(project_dir, 'dist', 'AnimatedCursorBuddy', 'AnimatedCursorBuddy.exe')}")
        print("=======================================================\n")
        
        # Install desktop and start menu shortcuts
        try:
            import install_shortcuts
            install_shortcuts.install_shortcuts()
        except Exception as e:
            print(f"[Build] Note: Could not auto-install shortcuts: {e}")
    else:
        print(f"\n[ERROR] Build failed with return code {res.returncode}")


if __name__ == "__main__":
    build()
