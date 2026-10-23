@echo off
setlocal
title Animated Cursor Buddy

:: Check if python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ and make sure 'Add Python to PATH' is checked.
    pause
    exit /b 1
)

:: Run Animated Cursor Buddy
python "%~dp0main.py" %*
