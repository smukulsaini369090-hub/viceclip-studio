"""
VICECLIP STUDIO — Telemetry & VRAM SSE Stream
===============================================
Streams real-time pipeline events, stage transitions, and live RTX 3050
VRAM telemetry (`used_mb`, `total_mb: 6144`) using Server-Sent Events (SSE).
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.core.vram_manager import get_vram_manager, get_vram_usage_mb

logger = logging.getLogger("viceclip.api.telemetry")

router = APIRouter(prefix="/api/events", tags=["Telemetry"])

# Global broadcast queue pool for active SSE clients
_subscribers: list[asyncio.Queue] = []


def broadcast_telemetry_sync(event: dict) -> None:
    """Non-async helper to broadcast event to all connected SSE clients."""
    for q in _subscribers[:]:
        try:
            q.put_nowait(event)
        except asyncio.QueueFull:
            pass


async def broadcast_telemetry(event: dict) -> None:
    """Async helper to broadcast event to all connected SSE clients."""
    broadcast_telemetry_sync(event)


@router.get("/stream")
async def event_stream() -> EventSourceResponse:
    """
    Server-Sent Events endpoint streaming real-time pipeline updates and VRAM stats:
      - Stage transitions (`whisper_gpu`, `demucs_gpu`, `mediapipe_gpu`, `nvenc_render`)
      - Progress percentage (0 - 100%)
      - ETA and log stream
      - Live RTX 3050 VRAM gauge (`used_mb`, `total_mb`, `utilization_pct`)
    """
    q: asyncio.Queue = asyncio.Queue(maxsize=128)
    _subscribers.append(q)

    mgr = get_vram_manager()

    async def event_generator() -> AsyncGenerator[dict, None]:
        try:
            while True:
                # Poll for pipeline event or push periodic VRAM heartbeat every 1 second
                try:
                    event = await asyncio.wait_for(q.get(), timeout=1.0)
                    yield {
                        "event": "pipeline_event",
                        "data": json.dumps(event),
                    }
                except asyncio.TimeoutError:
                    # Heartbeat with current VRAM status
                    vram_stat = mgr.get_vram_status()
                    yield {
                        "event": "vram_heartbeat",
                        "data": json.dumps(vram_stat),
                    }
        except asyncio.CancelledError:
            pass
        finally:
            if q in _subscribers:
                _subscribers.remove(q)

    return EventSourceResponse(event_generator())
