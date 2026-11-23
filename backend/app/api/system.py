"""
VICECLIP STUDIO — System, Settings & Explorer API
===================================================
Hardware status, Gemini connection testing, settings management,
Upload Kit retrieval, and Windows Explorer folder opener.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings
from app.core.gemini_brain import test_gemini_connection
from app.core.vram_manager import get_vram_usage_mb
from app.db.database import get_db
from app.db.models import (
    GeminiTestResult,
    SettingsResponse,
    SystemStatus,
    UploadKit,
)

logger = logging.getLogger("viceclip.api.system")

router = APIRouter(prefix="/api", tags=["System & Settings"])


class UpdateSettingsRequest(BaseModel):
    """Payload to update application settings."""
    gemini_api_key: Optional[str] = None
    gemini_fast_model: Optional[str] = None
    gemini_deep_model: Optional[str] = None
    whisper_model_size: Optional[str] = None
    nvenc_preset: Optional[str] = None
    target_fps: Optional[int] = None
    caption_theme: Optional[str] = None


class OpenFolderRequest(BaseModel):
    """Payload to launch Windows Explorer."""
    clip_id: Optional[str] = None
    video_id: Optional[str] = None


@router.get("/status", response_model=SystemStatus)
async def get_system_status() -> SystemStatus:
    """Returns live hardware capabilities, encoder status, and VRAM capacity."""
    cfg = get_settings()
    caps = cfg.check_capabilities()
    used_mb, total_mb = get_vram_usage_mb()

    return SystemStatus(
        ffmpeg_available=caps["ffmpeg"],
        nvenc_available=caps["nvenc"],
        cuda_available=caps["cuda"],
        cuda_device=caps["cuda_device"],
        vram_total_mb=total_mb,
        encoder=caps["encoder"],
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        workspace_dir=cfg.workspace_dir,
    )


@router.get("/settings", response_model=SettingsResponse)
async def get_settings_endpoint() -> SettingsResponse:
    """Returns safe current configuration options."""
    cfg = get_settings()
    return SettingsResponse(
        gemini_api_key_set=bool(cfg.gemini_api_key),
        gemini_fast_model=cfg.gemini_fast_model,
        gemini_deep_model=cfg.gemini_deep_model,
        whisper_model_size=cfg.whisper_model_size,
        nvenc_preset=cfg.nvenc_preset,
        target_fps=cfg.target_fps,
        caption_theme="vice_city_neon",
        output_dir=cfg.output_dir,
    )


@router.post("/settings")
async def update_settings_endpoint(req: UpdateSettingsRequest) -> dict:
    """Updates runtime configuration settings."""
    cfg = get_settings()
    if req.gemini_api_key is not None:
        cfg.gemini_api_key = req.gemini_api_key.strip()
    if req.gemini_fast_model:
        cfg.gemini_fast_model = req.gemini_fast_model.strip()
    if req.gemini_deep_model:
        cfg.gemini_deep_model = req.gemini_deep_model.strip()
    if req.whisper_model_size:
        cfg.whisper_model_size = req.whisper_model_size.strip()
    if req.nvenc_preset:
        cfg.nvenc_preset = req.nvenc_preset.strip()
    if req.target_fps:
        cfg.target_fps = req.target_fps

    return {"success": True, "message": "Settings updated successfully"}


@router.get("/gemini/test", response_model=GeminiTestResult)
async def test_gemini_endpoint() -> GeminiTestResult:
    """Validates the configured Gemini API key and enumerates available models."""
    return await test_gemini_connection()


@router.post("/open-output-folder")
async def open_output_folder_endpoint(req: OpenFolderRequest) -> dict:
    """
    Opens Windows Explorer directly at the output folder or highlights a rendered file.
    """
    cfg = get_settings()
    target_path = Path(cfg.output_dir).resolve()

    if req.video_id:
        clip_dir = target_path / "clips" / req.video_id
        if clip_dir.is_dir():
            target_path = clip_dir

    if req.clip_id and req.video_id:
        variant_a = target_path / f"{req.clip_id}_variant_A.mp4"
        if variant_a.is_file():
            # Highlight file in Windows Explorer
            if sys.platform == "win32":
                subprocess.Popen(["explorer.exe", f"/select,{str(variant_a)}"])
                return {"success": True, "path": str(variant_a)}

    # Open folder
    if sys.platform == "win32":
        subprocess.Popen(["explorer.exe", str(target_path)])
    else:
        logger.info("Non-Windows OS: output path is %s", target_path)

    return {"success": True, "path": str(target_path)}


@router.get("/upload-kit/{clip_id}")
async def get_upload_kit_endpoint(clip_id: str) -> dict:
    """Retrieves 1-Click Upload Kit metadata for a specific clip."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM clip_candidates WHERE clip_id = ?", (clip_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Clip {clip_id} not found")

    clip = dict(row)
    upload_kit_raw = clip.get("upload_kit_json", "{}")
    kit_data = json.loads(upload_kit_raw) if isinstance(upload_kit_raw, str) else upload_kit_raw

    return {
        "success": True,
        "clip_id": clip_id,
        "title_hook": clip.get("title_hook", ""),
        "upload_kit": kit_data,
        "cover_path": clip.get("cover_path", ""),
        "output_path_a": clip.get("output_path_a", ""),
        "output_path_b": clip.get("output_path_b", ""),
    }


@router.patch("/upload-kit/{clip_id}")
async def update_upload_kit_endpoint(clip_id: str, kit: UploadKit) -> dict:
    """Updates custom titles, hashtags, or pinned comment for a clip."""
    db = await get_db()
    await db.execute(
        "UPDATE clip_candidates SET upload_kit_json = ? WHERE clip_id = ?",
        (json.dumps(kit.model_dump()), clip_id),
    )
    await db.commit()
    return {"success": True, "message": f"Upload Kit for {clip_id} updated"}
