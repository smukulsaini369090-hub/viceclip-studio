"""
VICECLIP STUDIO — Analysis & Smart Cache API
==============================================
Endpoints for video intelligence analysis, Gemini manual JSON parsing,
and SQLite Smart Cache management.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.api.telemetry import broadcast_telemetry
from app.core.gemini_brain import parse_manual_response
from app.core.yt_extractor import normalize_video_id
from app.db.database import (
    cache_delete_video,
    cache_get_video,
    cache_list_videos,
    clips_get_by_video,
    clips_save_candidates,
)
from app.db.models import AnalyzeRequest, ManualGeminiInput
from app.services.pipeline import run_analysis_pipeline

logger = logging.getLogger("viceclip.api.analysis")

router = APIRouter(prefix="/api", tags=["Analysis & Cache"])


@router.post("/analyze")
async def analyze_video_endpoint(req: AnalyzeRequest) -> dict:
    """
    Analyzes a YouTube video via Pass 1 & Pass 2:
      - Returns cached intelligence immediately if previously processed.
      - Otherwise downloads media, transcribes with CUDA Whisper, detects audio/visual
        spikes, and queries Gemini Viral Brain (or generates manual prompt).
    """
    try:
        result = await run_analysis_pipeline(
            url=req.url,
            settings=req.settings,
            telemetry_cb=broadcast_telemetry,
        )
        return {"success": True, **result}
    except Exception as exc:
        logger.exception("Analysis pipeline failed for %s: %s", req.url, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/manual-gemini/parse")
async def parse_manual_gemini_endpoint(
    video_id: str = Query(..., description="Target YouTube Video ID"),
    payload: ManualGeminiInput = ...,
) -> dict:
    """
    Parses and validates raw JSON response pasted from `gemini.google.com`:
      - Automatically strips markdown fences, conversational prose, and trailing commas.
      - Validates against Pydantic ViralBrainResponse schema.
      - Saves candidate clips into SQLite Smart Cache.
    """
    cached = await cache_get_video(video_id)
    if not cached:
        raise HTTPException(status_code=404, detail=f"Video {video_id} not found in cache")

    try:
        parsed_response = parse_manual_response(payload.json_text)
        clips_dicts = [c.model_dump() for c in parsed_response.clips]

        await clips_save_candidates(video_id, clips_dicts)
        saved_clips = await clips_get_by_video(video_id)

        logger.info("Successfully parsed and saved %d clips for %s from Gemini Web JSON", len(saved_clips), video_id)
        return {
            "success": True,
            "video_id": video_id,
            "clips": saved_clips,
            "analysis_summary": parsed_response.analysis_summary,
            "video_type": parsed_response.video_type,
        }
    except Exception as exc:
        logger.error("Failed to parse manual Gemini JSON for %s: %s", video_id, exc)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Gemini response format: {exc}. Ensure the full JSON object is pasted."
        )


@router.get("/cache")
async def list_cache_endpoint(limit: int = Query(50, ge=1, le=100)) -> dict:
    """Returns list of previously analyzed videos from SQLite Smart Cache."""
    videos = await cache_list_videos(limit=limit)
    return {"success": True, "count": len(videos), "videos": videos}


@router.get("/cache/{video_id}")
async def get_cached_video_endpoint(video_id: str) -> dict:
    """Retrieves full cached intelligence and candidate clips for a single video."""
    video = await cache_get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video {video_id} not found in cache")

    clips = await clips_get_by_video(video_id)
    return {
        "success": True,
        "video": video,
        "clips": clips,
    }


@router.delete("/cache/{video_id}")
async def delete_cached_video_endpoint(video_id: str) -> dict:
    """Deletes a video and all its candidate clips from the SQLite Smart Cache."""
    await cache_delete_video(video_id)
    return {"success": True, "message": f"Video {video_id} removed from cache"}
