"""
Creates or removes Windows Desktop and Start Menu shortcuts with custom app icons.
"""

import argparse
import os
import sys
import win32com.client


def install_shortcuts():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(project_dir, "assets", "icon.ico")
    main_py = os.path.join(project_dir, "main.py")

    # Determine executable and arguments
    onedir_exe = os.path.join(project_dir, "dist", "AnimatedCursorBuddy", "AnimatedCursorBuddy.exe")
    onefile_exe = os.path.join(project_dir, "dist", "AnimatedCursorBuddy.exe")

    if os.path.exists(onedir_exe):
        target_path = onedir_exe
        arguments = ""
    elif os.path.exists(onefile_exe):
        target_path = onefile_exe
        arguments = ""
    else:
        # Use pythonw.exe to run without a command prompt
        python_exe = sys.executable
        pythonw_exe = os.path.join(os.path.dirname(python_exe), "pythonw.exe")
        if not os.path.exists(pythonw_exe):
            pythonw_exe = python_exe
        target_path = pythonw_exe
        arguments = f'"{main_py}"'

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut_locations = {
        "Desktop": shell.SpecialFolders("Desktop"),
        "Start Menu": shell.SpecialFolders("Programs"),
    }

    created = []
    for loc_name, folder in shortcut_locations.items():
        shortcut_file = os.path.join(folder, "Animated Cursor Buddy.lnk")
        shortcut = shell.CreateShortCut(shortcut_file)
        shortcut.TargetPath = target_path
        if arguments:
            shortcut.Arguments = arguments
        shortcut.WorkingDirectory = project_dir
        shortcut.Description = "Animated Cursor Buddy - Interactive Desktop Companion"
        if os.path.exists(icon_path):
            shortcut.IconLocation = f"{icon_path},0"
        shortcut.Save()
        created.append(shortcut_file)
        print(f"[Shortcut] Created {loc_name} shortcut: {shortcut_file}")

    return created


def remove_shortcuts():
    shell = win32com.client.Dispatch("WScript.Shell")
    folders = [shell.SpecialFolders("Desktop"), shell.SpecialFolders("Programs")]
    for folder in folders:
        lnk = os.path.join(folder, "Animated Cursor Buddy.lnk")
        if os.path.exists(lnk):
            try:
                os.remove(lnk)
                print(f"[Shortcut] Removed: {lnk}")
            except Exception as e:
                print(f"[Shortcut] Failed to remove {lnk}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Install Cursor Buddy Windows Shortcuts")
    parser.add_argument("--remove", action="store_true", help="Remove installed shortcuts")
    args = parser.parse_args()

    if args.remove:
        remove_shortcuts()
    else:
        install_shortcuts()


if __name__ == "__main__":
    main()
