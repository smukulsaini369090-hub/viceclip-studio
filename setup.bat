@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM  VICECLIP STUDIO — 1-Click Setup Launcher
REM  Initializes Python venv, PyTorch CUDA 12.4, requirements, default audio assets,
REM  and Next.js dependencies.
REM ═══════════════════════════════════════════════════════════════════════════════

title VICECLIP STUDIO — Installer
cd /d "%~dp0"

echo.
echo   ================================================================
echo     ██╗   ██╗██╗ ██████╗███████╗ ██████╗██╗     ██╗██████╗
echo     ██║   ██║██║██╔════╝██╔════╝██╔════╝██║     ██║██╔══██╗
echo     ██║   ██║██║██║     █████╗  ██║     ██║     ██║██████╔╝
echo     ╚██╗ ██╔╝██║██║     ██╔══╝  ██║     ██║     ██║██╔═══╝
echo      ╚████╔╝ ██║╚██████╗███████╗╚██████╗███████╗██║██║
echo       ╚═══╝  ╚═╝ ╚═════╝╚══════╝ ╚═════╝╚══════╝╚═╝╚═╝
echo                 I   N   S   T   A   L   L   E   R
echo   ================================================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERROR] Python is not installed or not in PATH!
    echo   Please install Python 3.11 or 3.12 from https://www.python.org/
    echo   (Make sure to check "Add Python to PATH" during installation)
    echo.
    pause
    exit /b 1
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERROR] Node.js is not installed or not in PATH!
    echo   Please install Node.js (v18+) from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo   Starting full environment setup via PowerShell...
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

if %errorlevel% neq 0 (
    echo.
    echo   [ERROR] Setup encountered an issue. See details above.
    pause
    exit /b %errorlevel%
)

echo.
echo   ================================================================
echo     SETUP COMPLETE! You can now start the studio:
echo       1. Double-click "start.bat"
echo       2. Your browser will open at http://localhost:3000
echo   ================================================================
echo.
pause
