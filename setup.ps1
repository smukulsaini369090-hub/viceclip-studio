<#
.SYNOPSIS
    VICECLIP STUDIO — Automated Environment Setup (Windows 11 / 10)

.DESCRIPTION
    1. Verifies Python 3.11+ and creates isolated .venv
    2. Auto-detects NVIDIA GPU (RTX series) and installs PyTorch CUDA 12.4
    3. Installs backend dependencies from backend/requirements.txt
    4. Auto-detects / checks Gyan FFmpeg 9.1 with NVENC support
    5. Generates default royalty-free SFX & synthwave audio loops
    6. Installs Next.js 14 frontend dependencies via npm
    7. Creates .env configuration from .env.example
#>

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = (Get-Location).Path }
Set-Location $ProjectRoot

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "====================================================================" -ForegroundColor DarkCyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "====================================================================" -ForegroundColor DarkCyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "  [WARN] $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "  [FAIL] $Message" -ForegroundColor Red
}

Write-Host ""
Write-Host "  ██╗   ██╗██╗ ██████╗███████╗ ██████╗██╗     ██╗██████╗ " -ForegroundColor Magenta
Write-Host "  ██║   ██║██║██╔════╝██╔════╝██╔════╝██║     ██║██╔══██╗" -ForegroundColor Magenta
Write-Host "  ██║   ██║██║██║     █████╗  ██║     ██║     ██║██████╔╝" -ForegroundColor Magenta
Write-Host "  ╚██╗ ██╔╝██║██║     ██╔══╝  ██║     ██║     ██║██╔═══╝ " -ForegroundColor Magenta
Write-Host "   ╚████╔╝ ██║╚██████╗███████╗╚██████╗███████╗██║██║     " -ForegroundColor Magenta
Write-Host "    ╚═══╝  ╚═╝ ╚═════╝╚══════╝ ╚═════╝╚══════╝╚═╝╚═╝     " -ForegroundColor Magenta
Write-Host "              S   T   U   D   I   O                        " -ForegroundColor DarkMagenta
Write-Host "        Universal Windows 10/11 Setup Installer            " -ForegroundColor DarkGray
Write-Host ""

# ── 1. PYTHON CHECK ──────────────────────────────────────────────────────────
Write-Step "1/7  Checking Python Environment"

$PythonCmd = $null
foreach ($candidate in @("python", "python3", "py -3")) {
    try {
        $parts = $candidate.Split(" ")
        $cmdName = $parts[0]
        $cmdArgs = if ($parts.Length -gt 1) { $parts[1..($parts.Length - 1)] } else { @() }
        $ver = & $cmdName @cmdArgs --version 2>&1
        if ($ver -match "Python 3\.(\d+)") {
            $minor = [int]$Matches[1]
            if ($minor -ge 11) {
                $PythonCmd = $candidate
                Write-Ok "Found Python: $ver"
                break
            }
        }
    } catch { }
}

if (-not $PythonCmd) {
    Write-Fail "Python 3.11 or higher is required."
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Gray
    Write-Host "  Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Gray
    exit 1
}

# ── 2. VIRTUAL ENVIRONMENT ───────────────────────────────────────────────────
Write-Step "2/7  Configuring Virtual Environment (.venv)"

$VenvDir = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$VenvPip = Join-Path $VenvDir "Scripts\pip.exe"

if (Test-Path $VenvPython) {
    Write-Ok "Existing .venv detected at $VenvDir"
} else {
    Write-Host "  Creating isolated virtual environment..." -ForegroundColor Gray
    $parts = $PythonCmd.Split(" ")
    $cmdName = $parts[0]
    $cmdArgs = if ($parts.Length -gt 1) { $parts[1..($parts.Length - 1)] } else { @() }
    & $cmdName @cmdArgs -m venv $VenvDir
    if (-not (Test-Path $VenvPython)) {
        Write-Fail "Failed to initialize .venv"
        exit 1
    }
    Write-Ok "Created virtual environment in .venv"
}

Write-Host "  Upgrading pip, setuptools, and wheel..." -ForegroundColor Gray
& $VenvPython -m pip install --upgrade pip setuptools wheel --quiet

# ── 3. PYTORCH CUDA / CPU DETECTION ──────────────────────────────────────────
Write-Step "3/7  Hardware Detection & PyTorch Installation"

$hasNvidia = $false
try {
    $gpuCheck = & nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>&1
    if ($LASTEXITCODE -eq 0 -and $gpuCheck) {
        $hasNvidia = $true
        Write-Ok "NVIDIA GPU Detected: $gpuCheck"
    }
} catch { }

$torchInstalled = $false
try {
    $tCheck = & $VenvPython -c "import torch; print(torch.__version__, torch.cuda.is_available())" 2>&1
    if ($tCheck -match "True") {
        $torchInstalled = $true
        Write-Ok "PyTorch CUDA already operational ($tCheck)"
    }
} catch { }

if (-not $torchInstalled) {
    if ($hasNvidia) {
        Write-Host "  Installing PyTorch with CUDA 12.4 acceleration..." -ForegroundColor Gray
        & $VenvPip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
    } else {
        Write-Warn "No NVIDIA GPU detected. Installing PyTorch CPU fallback..."
        & $VenvPip install torch torchvision torchaudio
    }
    Write-Ok "PyTorch installed successfully"
}

# ── 4. BACKEND DEPENDENCIES ──────────────────────────────────────────────────
Write-Step "4/7  Installing Backend Python Requirements"

$reqFile = Join-Path $ProjectRoot "backend\requirements.txt"
if (Test-Path $reqFile) {
    & $VenvPip install -r $reqFile
    Write-Ok "Backend dependencies installed"
} else {
    Write-Fail "backend\requirements.txt not found!"
    exit 1
}

# ── 5. FFMPEG & NVENC CHECK ──────────────────────────────────────────────────
Write-Step "5/7  Checking FFmpeg & Video Encoders"

$ffmpegFound = $false
try {
    $ffVer = & ffmpeg -version 2>&1 | Select-Object -First 1
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "FFmpeg detected in PATH: $ffVer"
        $ffmpegFound = $true
    }
} catch { }

if (-not $ffmpegFound) {
    $wingetDir = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
    if (Test-Path $wingetDir) {
        $candidate = Get-ChildItem -Path $wingetDir -Filter "ffmpeg.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($candidate) {
            Write-Ok "Discovered Gyan FFmpeg: $($candidate.FullName)"
            $ffmpegFound = $true
        }
    }
}

if (-not $ffmpegFound) {
    Write-Warn "FFmpeg is not installed or not in system PATH."
    Write-Host "  You can install it automatically in 1 click via PowerShell:" -ForegroundColor Yellow
    Write-Host "    winget install Gyan.FFmpeg" -ForegroundColor Cyan
    Write-Host "  (The backend will auto-detect Gyan FFmpeg once installed)." -ForegroundColor Gray
}

# ── 6. DEFAULT AUDIO ASSETS ──────────────────────────────────────────────────
Write-Step "6/7  Generating Default Audio SFX & Synthwave Assets"

$assetScript = Join-Path $ProjectRoot "backend\scripts\generate_default_assets.py"
if (Test-Path $assetScript) {
    $env:PYTHONPATH = "backend"
    & $VenvPython $assetScript
    Write-Ok "Default audio assets generated in assets/"
} else {
    Write-Warn "generate_default_assets.py not found — skipping asset generation"
}

# ── 7. FRONTEND NODE.JS CHECK & NPM INSTALL ──────────────────────────────────
Write-Step "7/7  Configuring Next.js Studio Frontend"

$nodeFound = $false
try {
    $nVer = & node --version 2>&1
    Write-Ok "Node.js detected: $nVer"
    $nodeFound = $true
} catch {
    Write-Warn "Node.js not found in PATH."
    Write-Host "  Download and install Node.js (v18+) from: https://nodejs.org/" -ForegroundColor Gray
}

$frontendDir = Join-Path $ProjectRoot "frontend"
if ($nodeFound -and (Test-Path (Join-Path $frontendDir "package.json"))) {
    Write-Host "  Installing frontend npm packages..." -ForegroundColor Gray
    Push-Location $frontendDir
    npm install
    Pop-Location
    Write-Ok "Frontend packages installed successfully"
}

# ── .ENV INITIALIZATION ──────────────────────────────────────────────────────
$envFile = Join-Path $ProjectRoot ".env"
$envExample = Join-Path $ProjectRoot ".env.example"
if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
    Copy-Item $envExample $envFile
    Write-Ok "Initialized .env configuration from .env.example"
}

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Green
Write-Host "  [OK] VICECLIP STUDIO SETUP COMPLETE!" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Quick Launch:" -ForegroundColor White
Write-Host "    Double-click 'start.bat' to launch both backend & frontend." -ForegroundColor Green
Write-Host "    Studio will open in your browser at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
