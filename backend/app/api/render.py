"""
VICECLIP STUDIO — Render API
==============================
Endpoints for triggering hardware-accelerated 1080x1920 Short renders
with custom crop overrides, trim adjustments, and dual-hook variants.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.telemetry import broadcast_telemetry
from app.db.models import CropOverride, RenderSettings, TrimAdjustment
from app.services.pipeline import run_render_pipeline

logger = logging.getLogger("viceclip.api.render")

router = APIRouter(prefix="/api/render", tags=["Render"])


class RenderClipRequest(BaseModel):
    """Payload to trigger export for a single candidate clip."""
    video_id: str = Field(description="YouTube Video ID")
    clip_id: str = Field(description="Candidate Clip ID")
    settings: Optional[RenderSettings] = None
    trim: Optional[TrimAdjustment] = None
    custom_crop: Optional[CropOverride] = None


class RenderMultipleRequest(BaseModel):
    """Payload to render multiple candidate clips sequentially."""
    video_id: str
    clip_ids: list[str] = Field(min_length=1)
    settings: Optional[RenderSettings] = None


@router.post("/clip")
async def render_clip_endpoint(req: RenderClipRequest) -> dict:
    """
    Renders a studio-grade 1080x1920 YouTube Short:
      - Uses h264_nvenc GPU encoding (or libx264 CPU fallback).
      - Applies 9:16 layout (Facecam/Gameplay split or action crop).
      - Renders animated ASS subtitles in selected theme.
      - Exports Variant A & Variant B for dual-hook testing.
      - Extracts high-contrast Shorts cover PNG frame.
    """
    try:
        result = await run_render_pipeline(
            video_id=req.video_id,
            clip_id=req.clip_id,
            settings=req.settings,
            custom_crop=req.custom_crop,
            trim=req.trim,
            telemetry_cb=broadcast_telemetry,
        )
        return {"success": True, **result}
    except Exception as exc:
        logger.exception("Render failed for clip %s (%s): %s", req.clip_id, req.video_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/batch")
async def render_multiple_endpoint(req: RenderMultipleRequest) -> dict:
    """Renders multiple candidate clips for a video sequentially."""
    results: list[dict] = []
    errors: list[dict] = []

    for cid in req.clip_ids:
        try:
            res = await run_render_pipeline(
                video_id=req.video_id,
                clip_id=cid,
                settings=req.settings,
                telemetry_cb=broadcast_telemetry,
            )
            results.append(res)
        except Exception as exc:
            logger.error("Failed to render clip %s: %s", cid, exc)
            errors.append({"clip_id": cid, "error": str(exc)})

    return {
        "success": len(errors) == 0,
        "rendered_count": len(results),
        "results": results,
        "errors": errors,
    }
