"""
VICECLIP STUDIO — Application Configuration
==============================================
Pydantic v2 Settings with:
  • Windows-safe path normalization & FFmpeg filter escaping
  • NVENC hardware capability check (synthetic encode test)
  • CUDA / pynvml VRAM detection with nvidia-smi fallback
"""

from __future__ import annotations

import logging
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger("viceclip.config")

_WIN_CREATE_NO_WINDOW: int = 0x08000000 if sys.platform == "win32" else 0


# ═══════════════════════════════════════════════════════════════════════════════
# HARDWARE CAPABILITY PROBES
# ═══════════════════════════════════════════════════════════════════════════════


def _run_silent(cmd: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
    """Run a subprocess with no visible console window on Windows."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=_WIN_CREATE_NO_WINDOW,
    )


def check_ffmpeg_available(ffmpeg_path: str = "ffmpeg") -> bool:
    """Return True if FFmpeg is reachable."""
    try:
        return _run_silent([ffmpeg_path, "-version"]).returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def check_nvenc_available(ffmpeg_path: str = "ffmpeg") -> bool:
    """
    Return True only if h264_nvenc is listed **and** a real 1-frame encode succeeds.
    This catches driver / NVENC session-limit issues that a simple -encoders check misses.
    """
    try:
        result = _run_silent([ffmpeg_path, "-encoders"])
        if "h264_nvenc" not in result.stdout:
            return False

        test_cmd = [
            ffmpeg_path, "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", "color=black:s=192x192:d=0.1:r=1",
            "-frames:v", "1",
            "-c:v", "h264_nvenc", "-preset", "p1",
            "-f", "null", "-",
        ]
        return _run_silent(test_cmd).returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def check_cuda_available() -> bool:
    """Return True if PyTorch reports CUDA availability."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def get_cuda_device_name() -> Optional[str]:
    """Return the CUDA device name, or None."""
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except ImportError:
        pass
    return None


def get_vram_total_mb() -> int:
    """
    Total GPU VRAM in MB.  Tries pynvml first, falls back to nvidia-smi,
    then defaults to 6144 (RTX 3050 Laptop).
    """
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        total = int(info.total / (1024 * 1024))
        pynvml.nvmlShutdown()
        return total
    except Exception:
        pass

    try:
        result = _run_silent(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"]
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError, ValueError):
        pass

    return 6144  # safe default for RTX 3050 Laptop


# ═══════════════════════════════════════════════════════════════════════════════
# SETTINGS MODEL
# ═══════════════════════════════════════════════════════════════════════════════


class ViceClipSettings(BaseSettings):
    """Central configuration loaded from ``.env`` with sane Windows defaults."""

    # ── Gemini API ────────────────────────────────────────────────────────────
    gemini_api_key: str = Field(default="", description="Gemini API key")
    gemini_fast_model: str = Field(default="gemini-3.5-flash-lite")
    gemini_deep_model: str = Field(default="gemini-3.5-flash-lite")

    # ── Paths ────────────────────────────────────────────────────────────────
    workspace_dir: str = Field(default="")
    output_dir: str = Field(default="")
    cache_dir: str = Field(default="")
    assets_dir: str = Field(default="")

    # ── FFmpeg / Encoding ────────────────────────────────────────────────────
    ffmpeg_path: str = Field(default="ffmpeg")
    ffprobe_path: str = Field(default="ffprobe")
    nvenc_preset: str = Field(default="p4")
    nvenc_cq: int = Field(default=19)
    nvenc_bitrate: str = Field(default="10M")
    target_fps: int = Field(default=60)

    # ── Whisper ──────────────────────────────────────────────────────────────
    whisper_model_size: str = Field(default="small")
    whisper_compute_type: str = Field(default="int8_float16")
    whisper_device: str = Field(default="cuda")

    # ── Server ───────────────────────────────────────────────────────────────
    backend_host: str = Field(default="127.0.0.1")
    backend_port: int = Field(default=8000)
    frontend_port: int = Field(default=3000)

    # ── Runtime capabilities (populated by check_capabilities) ───────────────
    _ffmpeg_available: bool = False
    _nvenc_available: bool = False
    _cuda_available: bool = False
    _cuda_device_name: Optional[str] = None
    _vram_total_mb: int = 6144

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    # ── post-init: resolve default paths ─────────────────────────────────────

    def model_post_init(self, __context: object) -> None:
        import os, shutil

        ws = Path(self.workspace_dir).resolve() if self.workspace_dir else Path(__file__).resolve().parent.parent.parent

        if not self.workspace_dir:
            self.workspace_dir = str(ws)
        if not self.output_dir:
            self.output_dir = str(ws / "output")
        if not self.cache_dir:
            self.cache_dir = str(ws / "cache")
        if not self.assets_dir:
            self.assets_dir = str(ws / "assets")

        for d in [
            self.output_dir,
            self.cache_dir,
            self.assets_dir,
            str(Path(self.assets_dir) / "music"),
            str(Path(self.assets_dir) / "sfx"),
            str(Path(self.output_dir) / "clips"),
            str(Path(self.output_dir) / "covers"),
        ]:
            Path(d).mkdir(parents=True, exist_ok=True)

        # Auto-discover FFmpeg if default or unreachable
        if not check_ffmpeg_available(self.ffmpeg_path):
            found = shutil.which("ffmpeg")
            if found and check_ffmpeg_available(found):
                self.ffmpeg_path = found
            else:
                winget = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"
                if winget.is_dir():
                    for p in winget.glob("**/ffmpeg.exe"):
                        if check_ffmpeg_available(str(p)):
                            self.ffmpeg_path = str(p)
                            break
                if not check_ffmpeg_available(self.ffmpeg_path):
                    for common in [
                        r"C:\ffmpeg\bin\ffmpeg.exe",
                        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                    ]:
                        if check_ffmpeg_available(common):
                            self.ffmpeg_path = common
                            break

        # If valid FFmpeg binary was discovered, prepend its directory to PATH
        if check_ffmpeg_available(self.ffmpeg_path):
            ffmpeg_dir = str(Path(self.ffmpeg_path).resolve().parent)
            current_path = os.environ.get("PATH", "")
            if ffmpeg_dir.lower() not in current_path.lower():
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + current_path

        # Run hardware scan immediately
        self.check_capabilities()

    # ── hardware capability scanner ──────────────────────────────────────────

    def check_capabilities(self) -> dict:
        """
        Run every hardware probe once at startup.
        Returns a summary dict suitable for the ``/api/status`` endpoint.
        """
        import os, shutil

        self._ffmpeg_available = check_ffmpeg_available(self.ffmpeg_path)
        if not self._ffmpeg_available:
            found = shutil.which("ffmpeg")
            if found and check_ffmpeg_available(found):
                self.ffmpeg_path = found
                self._ffmpeg_available = True
            else:
                winget = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"
                if winget.is_dir():
                    for p in winget.glob("**/ffmpeg.exe"):
                        if check_ffmpeg_available(str(p)):
                            self.ffmpeg_path = str(p)
                            self._ffmpeg_available = True
                            break
        if self._ffmpeg_available:
            ffmpeg_dir = str(Path(self.ffmpeg_path).resolve().parent)
            current_path = os.environ.get("PATH", "")
            if ffmpeg_dir.lower() not in current_path.lower():
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + current_path

        self._nvenc_available = (
            check_nvenc_available(self.ffmpeg_path) if self._ffmpeg_available else False
        )
        self._cuda_available = check_cuda_available()
        self._cuda_device_name = get_cuda_device_name()
        self._vram_total_mb = get_vram_total_mb()

        caps = {
            "ffmpeg": self._ffmpeg_available,
            "nvenc": self._nvenc_available,
            "cuda": self._cuda_available,
            "cuda_device": self._cuda_device_name,
            "vram_total_mb": self._vram_total_mb,
            "encoder": self.encoder,
        }
        logger.info("VICECLIP STUDIO capabilities: %s", caps)
        return caps

    # ── convenience properties ───────────────────────────────────────────────

    @property
    def ffmpeg_ok(self) -> bool:
        return self._ffmpeg_available

    @property
    def nvenc_ok(self) -> bool:
        return self._nvenc_available

    @property
    def cuda_ok(self) -> bool:
        return self._cuda_available

    @property
    def encoder(self) -> str:
        return "h264_nvenc" if self._nvenc_available else "libx264"

    @property
    def encoder_params(self) -> list[str]:
        """FFmpeg encoder CLI flags for the best available encoder."""
        if self._nvenc_available:
            return [
                "-c:v", "h264_nvenc",
                "-preset", self.nvenc_preset,
                "-rc", "vbr",
                "-cq", str(self.nvenc_cq),
                "-b:v", self.nvenc_bitrate,
            ]
        return ["-c:v", "libx264", "-preset", "medium", "-crf", "19"]

    @property
    def db_path(self) -> Path:
        return Path(self.cache_dir) / "viceclip_studio.db"

    @property
    def workspace_path(self) -> Path:
        return Path(self.workspace_dir).resolve()

    # ── FFmpeg path helpers ──────────────────────────────────────────────────

    def ffmpeg_safe_path(self, path: str | Path) -> str:
        """
        Convert a Windows path to FFmpeg-safe format for filter strings.

        Rules applied:
          1. Backslashes → forward slashes
          2. Drive-letter colon is escaped  ``C:`` → ``C\\:``
          3. Single quotes are escaped for FFmpeg filter quoting
        """
        s = str(Path(path).resolve()).replace("\\", "/")
        if len(s) >= 2 and s[1] == ":":
            s = s[0] + "\\:" + s[2:]
        s = s.replace("'", "'\\''")
        return s

    def ffmpeg_ass_path(self, path: str | Path) -> str:
        """
        Return a path safe for use inside ``ass=`` or ``subtitles=`` filter.
        Same as ffmpeg_safe_path but wrapped in single quotes for the filter.
        """
        return f"'{self.ffmpeg_safe_path(path)}'"


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON ACCESSOR
# ═══════════════════════════════════════════════════════════════════════════════


@lru_cache(maxsize=1)
def get_settings() -> ViceClipSettings:
    """Return the singleton ViceClipSettings instance."""
    return ViceClipSettings()
