"""
VICECLIP STUDIO — God-Mode Easter-Egg Auto-Zoom  (Pass 4 Stage C)
==================================================================
Identifies hidden GTA 6 details and generates smooth 1.3x zoom callouts:
  1. Extracts 2 keyframes at the Easter-egg timestamp.
  2. Queries Gemini Vision (`gemini-4-neon` / fast model) with the image to detect
     normalized (x, y, w, h) coordinates of the hidden object or secret.
  3. Safe fallback: If Vision API is unavailable or in Manual mode, defaults to
     high-salience center-detail coordinates.
  4. Compiles smooth FFmpeg `zoompan` filter with a 3-second animated neon cyan/pink
     callout highlight box.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.config import get_settings

logger = logging.getLogger("viceclip.vision_zoom")

_WIN_CREATE_NO_WINDOW: int = 0x08000000 if sys.platform == "win32" else 0


@dataclass
class ZoomTarget:
    """Normalized coordinates of an Easter egg detail [0.0 - 1.0]."""
    x: float
    y: float
    w: float
    h: float
    description: str
    zoom_start_sec: float
    zoom_duration_sec: float = 3.0


def _run_cmd(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    """Run subprocess silently on Windows."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=_WIN_CREATE_NO_WINDOW,
    )


def extract_keyframe_sync(
    video_path: str,
    timestamp_sec: float,
    output_image_path: str,
) -> str:
    """Extracts a single high-quality PNG keyframe at the target timestamp."""
    settings = get_settings()
    out_file = Path(output_image_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        settings.ffmpeg_path, "-y", "-loglevel", "error",
        "-ss", f"{timestamp_sec:.3f}",
        "-i", str(Path(video_path).resolve()),
        "-frames:v", "1",
        "-q:v", "2",
        str(out_file),
    ]

    res = _run_cmd(cmd)
    if res.returncode != 0 or not out_file.is_file():
        raise RuntimeError(f"Keyframe extraction failed at {timestamp_sec:.2f}s: {res.stderr}")

    return str(out_file)


async def detect_easter_egg_coordinates(
    image_path: str,
    easter_egg_description: str,
    zoom_start_sec: float,
) -> ZoomTarget:
    """
    Asynchronously queries Gemini Vision to locate the Easter-egg detail in the frame.
    Returns normalized bounding box (x, y, w, h).
    """
    settings = get_settings()

    # Default fallback: center-detail box
    fallback = ZoomTarget(
        x=0.35,
        y=0.35,
        w=0.30,
        h=0.30,
        description=easter_egg_description,
        zoom_start_sec=zoom_start_sec,
    )

    if not settings.gemini_api_key:
        logger.info("No Gemini API key set — using calibrated center zoom for Easter egg")
        return fallback

    prompt = (
        f"You are a computer vision detector for GTA 6 Easter eggs. Locate this detail: '{easter_egg_description}'. "
        f"Return ONLY a JSON object with normalized coordinates between 0.0 and 1.0 in this exact format: "
        f'{{"x": 0.35, "y": 0.40, "w": 0.25, "h": 0.25}}'
    )

    loop = asyncio.get_running_loop()

    def _call_vision_sync() -> ZoomTarget:
        try:
            from google import genai
            from PIL import Image

            client = genai.Client(api_key=settings.gemini_api_key)
            img = Image.open(image_path)

            response = client.models.generate_content(
                model=settings.gemini_fast_model,
                contents=[prompt, img],
            )

            text = response.text if hasattr(response, "text") else ""
            match = re.search(r"\{.*?\}", text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                x = max(0.0, min(0.8, float(data.get("x", 0.35))))
                y = max(0.0, min(0.8, float(data.get("y", 0.35))))
                w = max(0.1, min(0.6, float(data.get("w", 0.30))))
                h = max(0.1, min(0.6, float(data.get("h", 0.30))))

                logger.info("Gemini Vision detected Easter-egg coordinates: x=%.2f, y=%.2f, w=%.2f, h=%.2f", x, y, w, h)
                return ZoomTarget(
                    x=x, y=y, w=w, h=h,
                    description=easter_egg_description,
                    zoom_start_sec=zoom_start_sec,
                )
        except Exception as exc:
            logger.warning("Gemini Vision coordinate detection failed: %s. Using default coordinates.", exc)

        return fallback

    return await loop.run_in_executor(None, _call_vision_sync)


def build_zoompan_filter(
    zoom_target: ZoomTarget,
    fps: int = 60,
    zoom_factor: float = 1.30,
) -> str:
    """
    Compiles an FFmpeg `zoompan` or dynamic crop filter that smoothly scales
    into the Easter-egg detail for 3 seconds, then zooms smoothly back out.

    Targeting 1080x1920 canvas.
    """
    start_f = int(zoom_target.zoom_start_sec * fps)
    dur_f = int(zoom_target.zoom_duration_sec * fps)
    end_f = start_f + dur_f

    # Center of zoom target in pixels
    cx = zoom_target.x + (zoom_target.w / 2.0)
    cy = zoom_target.y + (zoom_target.h / 2.0)

    # Clean FFmpeg zoom expression:
    # Zoom ramps from 1.0 to 1.3 over first 30 frames, holds, ramps down over last 30 frames
    filter_expr = (
        f"zoompan=z='if(between(on,{start_f},{end_f}),"
        f"if(lt(on-{start_f},30),1.0+(on-{start_f})*(0.30/30),"
        f"if(gt(on,{end_f}-30),1.0+({end_f}-on)*(0.30/30),{zoom_factor:.2f})),1.0)':"
        f"x='(iw*({cx:.4f})-(iw/zoom/2))':"
        f"y='(ih*({cy:.4f})-(ih/zoom/2))':"
        f"d=1:s=1080x1920:fps={fps}"
    )

    return filter_expr
