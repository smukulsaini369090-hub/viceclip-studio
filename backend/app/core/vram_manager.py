"""
VICECLIP STUDIO — VRAM Manager
================================
Thread-safe async singleton that orchestrates GPU stages **one at a time**
on the RTX 3050 Laptop (6 GB VRAM strict ceiling).

Usage::

    from app.core.vram_manager import get_vram_manager, GPUStage

    mgr = get_vram_manager()
    async with mgr.acquire_gpu(GPUStage.WHISPER):
        # run Whisper model here — VRAM is exclusively yours
        ...
    # on exit the manager auto-flushes (del, gc, torch.cuda.empty_cache)
"""

from __future__ import annotations

import asyncio
import gc
import logging
import subprocess
import sys
import time
from contextlib import asynccontextmanager
from enum import Enum
from typing import AsyncGenerator, Optional

logger = logging.getLogger("viceclip.vram")

_WIN_CREATE_NO_WINDOW: int = 0x08000000 if sys.platform == "win32" else 0


# ═══════════════════════════════════════════════════════════════════════════════
# GPU STAGE ENUM
# ═══════════════════════════════════════════════════════════════════════════════


class GPUStage(str, Enum):
    """Named GPU pipeline stages (only one may hold the lock at a time)."""
    IDLE = "idle"
    WHISPER = "whisper_transcription"
    DEMUCS = "demucs_music_separation"
    MEDIAPIPE = "mediapipe_face_detection"
    GEMINI_VISION = "gemini_vision_zoom"
    EDGE_TTS = "edge_tts_synthesis"
    NVENC_RENDER = "nvenc_gpu_render"


# ═══════════════════════════════════════════════════════════════════════════════
# LOW-LEVEL GPU HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def flush_gpu_memory() -> None:
    """Force-flush GPU memory via PyTorch + Python garbage collector."""
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            logger.debug("torch.cuda.empty_cache() + synchronize() done")
    except ImportError:
        pass


def get_vram_usage_mb() -> tuple[int, int]:
    """
    Return ``(used_mb, total_mb)`` for GPU 0.

    Resolution order:
      1. ``pynvml`` (fastest, in-process)
      2. ``nvidia-smi`` CLI (subprocess fallback)
      3. ``(0, 6144)`` hardcoded default
    """
    # ── pynvml ───────────────────────────────────────────────────────────────
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        used = int(info.used / (1024 * 1024))
        total = int(info.total / (1024 * 1024))
        pynvml.nvmlShutdown()
        return used, total
    except Exception:
        pass

    # ── nvidia-smi fallback ──────────────────────────────────────────────────
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=_WIN_CREATE_NO_WINDOW,
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(",")
            return int(parts[0].strip()), int(parts[1].strip())
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError, ValueError):
        pass

    return 0, 6144


# ═══════════════════════════════════════════════════════════════════════════════
# VRAM MANAGER SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════


class VRAMManager:
    """
    Async-safe VRAM orchestrator.

    * Only **one** GPU stage runs at a time (enforced by an ``asyncio.Lock``).
    * VRAM is flushed **before** and **after** every stage.
    * Telemetry subscribers receive real-time stage-change events via
      ``asyncio.Queue`` (consumed by SSE endpoints in Milestone 4).
    """

    _instance: Optional[VRAMManager] = None

    def __new__(cls) -> VRAMManager:
        if cls._instance is None:
            inst = super().__new__(cls)
            inst._initialized = False
            cls._instance = inst
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._gpu_lock: Optional[asyncio.Lock] = None
        self._current_stage: GPUStage = GPUStage.IDLE
        self._stage_start_time: float = 0.0
        self._listeners: list[asyncio.Queue[dict]] = []
        logger.info("VRAMManager singleton initialised (RTX 3050 — 6 GB ceiling)")

    # ── lazy lock (must be created inside a running event loop) ───────────────

    def _ensure_lock(self) -> asyncio.Lock:
        if self._gpu_lock is None:
            self._gpu_lock = asyncio.Lock()
        return self._gpu_lock

    # ── public read-only state ───────────────────────────────────────────────

    @property
    def current_stage(self) -> GPUStage:
        return self._current_stage

    @property
    def is_busy(self) -> bool:
        return self._current_stage != GPUStage.IDLE

    @property
    def stage_elapsed_seconds(self) -> float:
        if self._current_stage == GPUStage.IDLE:
            return 0.0
        return time.time() - self._stage_start_time

    def get_vram_status(self) -> dict:
        """Snapshot for telemetry / SSE."""
        used_mb, total_mb = get_vram_usage_mb()
        return {
            "used_mb": used_mb,
            "total_mb": total_mb,
            "free_mb": total_mb - used_mb,
            "utilization_pct": round((used_mb / total_mb) * 100, 1) if total_mb > 0 else 0.0,
            "current_stage": self._current_stage.value,
            "stage_elapsed_sec": round(self.stage_elapsed_seconds, 1),
        }

    # ── telemetry pub/sub ────────────────────────────────────────────────────

    def subscribe_telemetry(self) -> asyncio.Queue[dict]:
        """Add a listener queue for stage events."""
        q: asyncio.Queue[dict] = asyncio.Queue(maxsize=256)
        self._listeners.append(q)
        return q

    def unsubscribe_telemetry(self, q: asyncio.Queue[dict]) -> None:
        """Remove a listener queue."""
        try:
            self._listeners.remove(q)
        except ValueError:
            pass

    async def _notify(self, event: dict) -> None:
        dead: list[asyncio.Queue[dict]] = []
        for q in self._listeners:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self._listeners.remove(q)

    # ── main context manager ─────────────────────────────────────────────────

    @asynccontextmanager
    async def acquire_gpu(self, stage: GPUStage) -> AsyncGenerator[None, None]:
        """
        Acquire **exclusive** GPU access for *stage*.

        * Blocks until any running stage releases the lock.
        * Flushes VRAM before yielding and again on exit.
        * Publishes ``stage_start`` / ``stage_end`` events to subscribers.
        """
        lock = self._ensure_lock()
        logger.info("[VRAM] Waiting for GPU lock — requested: %s", stage.value)

        await lock.acquire()
        try:
            # ── pre-flush ────────────────────────────────────────────────────
            flush_gpu_memory()

            self._current_stage = stage
            self._stage_start_time = time.time()

            status = self.get_vram_status()
            logger.info(
                "[VRAM] ▶ %s — VRAM %d MB / %d MB (%s%%)",
                stage.value,
                status["used_mb"],
                status["total_mb"],
                status["utilization_pct"],
            )
            await self._notify({"type": "stage_start", "stage": stage.value, **status})

            yield

        finally:
            elapsed = time.time() - self._stage_start_time
            logger.info("[VRAM] ■ %s finished in %.1fs — flushing", stage.value, elapsed)

            # ── post-flush ───────────────────────────────────────────────────
            flush_gpu_memory()

            self._current_stage = GPUStage.IDLE
            self._stage_start_time = 0.0

            post = self.get_vram_status()
            logger.info(
                "[VRAM] Post-flush — VRAM %d MB / %d MB", post["used_mb"], post["total_mb"]
            )
            await self._notify({
                "type": "stage_end",
                "stage": stage.value,
                "elapsed_sec": round(elapsed, 1),
                **post,
            })

            lock.release()

    # ── manual flush ─────────────────────────────────────────────────────────

    async def force_flush(self) -> dict:
        """Force an immediate VRAM flush (safe when idle)."""
        flush_gpu_memory()
        status = self.get_vram_status()
        logger.info(
            "[VRAM] Force flush — %d MB / %d MB", status["used_mb"], status["total_mb"]
        )
        return status


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC ACCESSOR
# ═══════════════════════════════════════════════════════════════════════════════


def get_vram_manager() -> VRAMManager:
    """Return the VRAMManager singleton."""
    return VRAMManager()
