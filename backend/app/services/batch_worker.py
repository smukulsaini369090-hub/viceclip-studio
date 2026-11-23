"""
VICECLIP STUDIO — Batch Watchlist Worker
==========================================
Background async service that runs continuous, unattended batch rendering
overnight for multi-video queues:
  1. Polls SQLite `job_queue` for pending jobs ordered by priority and creation time.
  2. For each queued item:
     - Downloads and analyzes the video via `run_analysis_pipeline`.
     - Automatically renders the top ranked candidate clips via `run_render_pipeline`.
     - Updates progress, current stage, and completion timestamps in SQLite.
     - Gracefully catches failures without crashing the queue runner.
  3. Clean shutdown support on FastAPI lifespan exit.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

from app.db.database import (
    clips_get_by_video,
    job_get_next_pending,
    job_update_status,
)
from app.db.models import RenderSettings
from app.services.pipeline import run_analysis_pipeline, run_render_pipeline

logger = logging.getLogger("viceclip.batch_worker")

_worker_task: Optional[asyncio.Task] = None
_stop_event = asyncio.Event()


async def _process_single_job(job: dict) -> None:
    """Processes a single dequeued job through analysis and automatic clip export."""
    job_id = job["id"]
    video_url = job["video_url"]
    settings_raw = job.get("settings_json", "{}")

    try:
        settings_dict = json.loads(settings_raw) if isinstance(settings_raw, str) else settings_raw
        settings = RenderSettings(**settings_dict)
    except Exception:
        settings = RenderSettings()

    logger.info("Batch worker started Job #%d: %s", job_id, video_url)
    await job_update_status(job_id, "processing", stage="Analyzing Video", progress=5.0)

    try:
        # Step 1: Run Analysis
        analysis_res = await run_analysis_pipeline(video_url, settings=settings)
        video_id = analysis_res["video_id"]

        await job_update_status(job_id, "processing", stage="Selecting Clips", progress=50.0)

        # Step 2: Auto-Render Top Candidates (up to 3 clips per video for batch mode)
        clips = await clips_get_by_video(video_id)
        clips_to_render = clips[:3]

        if not clips_to_render:
            logger.warning("No candidate clips found for Job #%d (%s)", job_id, video_id)
            await job_update_status(job_id, "completed", stage="Completed (No Clips)", progress=100.0)
            return

        total_clips = len(clips_to_render)
        for idx, clip in enumerate(clips_to_render):
            clip_id = clip["clip_id"]
            pct = 50.0 + ((idx + 1) / total_clips) * 45.0
            await job_update_status(
                job_id,
                "processing",
                stage=f"Rendering Clip {idx + 1}/{total_clips} ({clip_id})",
                progress=pct,
            )

            await run_render_pipeline(
                video_id=video_id,
                clip_id=clip_id,
                settings=settings,
            )

        await job_update_status(job_id, "completed", stage="Done", progress=100.0)
        logger.info("Batch worker successfully completed Job #%d (%d clips rendered)", job_id, total_clips)

    except Exception as exc:
        logger.exception("Batch worker failed on Job #%d: %s", job_id, exc)
        await job_update_status(
            job_id,
            "failed",
            stage="Error",
            progress=0.0,
            error=str(exc),
        )


async def _worker_loop() -> None:
    """Continuous polling loop."""
    logger.info("Batch Watchlist background worker started.")
    while not _stop_event.is_set():
        try:
            job = await job_get_next_pending()
            if job:
                await _process_single_job(job)
            else:
                # Idle wait when queue is empty
                try:
                    await asyncio.wait_for(_stop_event.wait(), timeout=3.0)
                except asyncio.TimeoutError:
                    pass
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.error("Unexpected error in batch worker loop: %s", exc)
            await asyncio.sleep(5.0)

    logger.info("Batch Watchlist background worker stopped cleanly.")


def start_batch_worker() -> None:
    """Launches the background worker task."""
    global _worker_task, _stop_event
    _stop_event.clear()
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(_worker_loop())


async def stop_batch_worker() -> None:
    """Signals and awaits graceful worker termination."""
    global _worker_task, _stop_event
    _stop_event.set()
    if _worker_task and not _worker_task.done():
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    _worker_task = None
