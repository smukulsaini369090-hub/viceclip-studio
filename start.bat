@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM  VICECLIP STUDIO — Production One-Click Launcher
REM  Automatically detects WinGet FFmpeg 9.1, cleans stale ports, launches
REM  FastAPI backend (127.0.0.1:8000) and Next.js frontend (localhost:3000),
REM  and opens the studio in your default browser.
REM ═══════════════════════════════════════════════════════════════════════════════

title VICECLIP STUDIO — Launcher
cd /d "%~dp0"

echo.
echo   ================================================================
echo     ██╗   ██╗██╗ ██████╗███████╗ ██████╗██╗     ██╗██████╗
echo     ██║   ██║██║██╔════╝██╔════╝██╔════╝██║     ██║██╔══██╗
echo     ██║   ██║██║██║     █████╗  ██║     ██║     ██║██████╔╝
echo     ╚██╗ ██╔╝██║██║     ██╔══╝  ██║     ██║     ██║██╔═══╝
echo      ╚████╔╝ ██║╚██████╗███████╗╚██████╗███████╗██║██║
echo       ╚═══╝  ╚═╝ ╚═════╝╚══════╝ ╚═════╝╚══════╝╚═╝╚═╝
echo                 S   T   U   D   I   O
echo   ================================================================
echo.

REM ── 1. Locate and Inject FFmpeg 9.1 into PATH ──────────────────────────────
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    for /d %%i in ("%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*") do (
        for /d %%j in ("%%i\ffmpeg-*") do (
            if exist "%%j\bin\ffmpeg.exe" (
                set "PATH=%%j\bin;%PATH%"
                echo   [OK] Injected FFmpeg binary: %%j\bin
            )
        )
    )
)

REM ── 2. Verify Python Virtual Environment ───────────────────────────────────
if not exist ".venv\Scripts\python.exe" (
    echo   [ERROR] Python virtual environment not found in .venv!
    echo   Please run setup first:
    echo     powershell -ExecutionPolicy Bypass -File setup.ps1
    echo.
    pause
    exit /b 1
)

REM ── 3. Kill any lingering processes on ports 8000 and 3000 ─────────────────
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /r ":8000\>"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /r ":3000\>"') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM ── 4. Launch FastAPI Backend ──────────────────────────────────────────────
echo   Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "VICECLIP STUDIO — Backend (FastAPI)" cmd /k "cd /d "%~dp0" && set PYTHONPATH=backend && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

REM ── 5. Wait for Backend initialization ─────────────────────────────────────
timeout /t 3 /nobreak >nul

REM ── 6. Launch Next.js Frontend ─────────────────────────────────────────────
if exist "frontend\package.json" (
    echo   Starting Next.js Studio on http://localhost:3000 ...
    start "VICECLIP STUDIO — Frontend (Next.js)" cmd /k "cd /d "%~dp0\frontend" && npm run dev"
)

REM ── 7. Wait and Open Browser ───────────────────────────────────────────────
timeout /t 4 /nobreak >nul
echo   Opening VICECLIP STUDIO in browser...
start "" "http://localhost:3000"

echo.
echo   ================================================================
echo     VICECLIP STUDIO IS RUNNING!
echo     • Web Studio: http://localhost:3000
echo     • Backend API: http://127.0.0.1:8000
echo     • Interactive API Docs: http://127.0.0.1:8000/docs
echo   ================================================================
echo.
echo   Keep this window open or minimize it.
echo.
