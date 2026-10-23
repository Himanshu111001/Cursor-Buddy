@echo off
setlocal
title Build Animated Cursor Buddy Executable

echo ===================================================
echo   Building Animated Cursor Buddy Standalone App
echo ===================================================

python "%~dp0build_exe.py"

pause
