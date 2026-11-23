"""
VICECLIP STUDIO — Batch Watchlist Queue API
=============================================
Endpoints for managing unattended overnight batch rendering queues.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.yt_extractor import normalize_video_id
from app.db.database import job_delete, job_enqueue, job_list_all
from app.db.models import BatchQueueRequest

logger = logging.getLogger("viceclip.api.batch")

router = APIRouter(prefix="/api/batch", tags=["Batch Queue"])


@router.get("")
async def list_batch_queue_endpoint(limit: int = Query(50, ge=1, le=200)) -> dict:
    """Returns all jobs in the batch watchlist queue."""
    jobs = await job_list_all(limit=limit)
    return {"success": True, "count": len(jobs), "jobs": jobs}


@router.post("")
@router.post("/add")
async def enqueue_batch_endpoint(req: BatchQueueRequest) -> dict:
    """
    Enqueues a list of YouTube URLs for unattended sequential overnight processing.
    """
    queued_ids: list[int] = []
    settings_json = json.dumps(req.settings.model_dump()) if req.settings else "{}"

    for url in req.urls:
        clean_url = url.strip()
        if not clean_url:
            continue
        try:
            vid = normalize_video_id(clean_url)
        except Exception:
            vid = ""

        jid = await job_enqueue(
            url=clean_url,
            video_id=vid,
            settings_json=settings_json,
            priority=0,
        )
        queued_ids.append(jid)

    logger.info("Enqueued %d videos into batch watchlist", len(queued_ids))
    return {
        "success": True,
        "enqueued_count": len(queued_ids),
        "job_ids": queued_ids,
        "message": f"Enqueued {len(queued_ids)} video(s) for batch processing",
    }


@router.delete("/{job_id}")
async def delete_job_endpoint(job_id: int) -> dict:
    """Removes a job from the batch queue."""
    await job_delete(job_id)
    return {"success": True, "message": f"Job #{job_id} removed from queue"}
