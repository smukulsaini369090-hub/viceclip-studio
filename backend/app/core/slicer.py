"""
VICECLIP STUDIO — Keyframe-Safe Slicer  (Pass 3)
==================================================
Extracts ONLY the selected candidate clips from the full-length source video
using FFmpeg fast seek + lossless stream-copy (`-c copy`) with a pre-roll buffer
(default 1.5 s).

Why Pre-Roll?
  Stream-copy seeking snaps to the nearest keyframe (I-frame). If seeking
  directly to `start_sec`, players or decoders can show frozen frames or audio
  desync until the next I-frame arrives.
  By extracting with a 1.5 s pre-roll buffer before `start_sec` and recording
  the exact `relative_start_sec`, downstream GPU render stages (NVENC) can
  trim precisely on an exact frame boundary without any frozen starting frames.
"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.config import get_settings

logger = logging.getLogger("viceclip.slicer")

_WIN_CREATE_NO_WINDOW: int = 0x08000000 if sys.platform == "win32" else 0


@dataclass
class SlicedClip:
    """Metadata describing an isolated candidate clip slice."""
    clip_id: str
    video_path: str
    audio_path: str
    source_start_sec: float
    source_end_sec: float
    slice_start_sec: float       # actual start time in source video where slice begins
    relative_start_sec: float    # offset from slice start to intended clip start (e.g., ~1.5s)
    relative_end_sec: float      # offset from slice start to intended clip end
    target_duration_sec: float   # intended clip duration (end_sec - start_sec)
    total_slice_duration_sec: float  # full slice duration including pre/post roll


def _run_cmd(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute subprocess synchronously without opening console windows on Windows."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=_WIN_CREATE_NO_WINDOW,
    )


def slice_clip_sync(
    source_video: str,
    source_audio: str,
    clip_id: str,
    start_sec: float,
    end_sec: float,
    output_dir: str,
    pre_roll_sec: float = 1.5,
    post_roll_sec: float = 1.0,
) -> SlicedClip:
    """
    Synchronously slices a single candidate clip with pre-roll buffer.
    Uses FFmpeg `-ss ... -i ... -t ... -c copy` for near-instant lossless extraction.
    """
    settings = get_settings()
    ffmpeg_bin = settings.ffmpeg_path

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    target_duration = max(0.5, end_sec - start_sec)

    # Calculate padded slice boundaries
    slice_start = max(0.0, start_sec - pre_roll_sec)
    actual_pre_roll = start_sec - slice_start
    slice_duration = target_duration + actual_pre_roll + post_roll_sec

    relative_start = actual_pre_roll
    relative_end = relative_start + target_duration

    sliced_video = str(out_dir / f"{clip_id}_slice.mp4")
    sliced_audio = str(out_dir / f"{clip_id}_slice.m4a")

    logger.info(
        "Slicing clip '%s': source [%.2fs - %.2fs] -> slice [%.2fs + %.2fs dur]",
        clip_id, start_sec, end_sec, slice_start, slice_duration
    )

    # 1. Slice video (lossless copy)
    cmd_video = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-ss", f"{slice_start:.3f}",
        "-i", str(Path(source_video).resolve()),
        "-t", f"{slice_duration:.3f}",
        "-c", "copy",
        "-avoid_negative_ts", "make_zero",
        sliced_video,
    ]
    res_v = _run_cmd(cmd_video)
    if res_v.returncode != 0:
        logger.warning(
            "Lossless video copy failed for '%s' (code %d): %s. Retrying with ultra-fast encode...",
            clip_id, res_v.returncode, res_v.stderr
        )
        # Fallback to fast transcode if stream copy fails on malformed keyframe
        cmd_video_fallback = [
            ffmpeg_bin, "-y", "-loglevel", "error",
            "-ss", f"{slice_start:.3f}",
            "-i", str(Path(source_video).resolve()),
            "-t", f"{slice_duration:.3f}",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
            "-c:a", "copy",
            "-avoid_negative_ts", "make_zero",
            sliced_video,
        ]
        res_v_fb = _run_cmd(cmd_video_fallback, timeout=120)
        if res_v_fb.returncode != 0:
            raise RuntimeError(f"FFmpeg video slice failed for {clip_id}: {res_v_fb.stderr}")

    # 2. Slice audio (lossless copy or extract from video if separate audio not present)
    audio_source = source_audio if (source_audio and os.path.isfile(source_audio)) else source_video
    cmd_audio = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-ss", f"{slice_start:.3f}",
        "-i", str(Path(audio_source).resolve()),
        "-t", f"{slice_duration:.3f}",
        "-vn",
        "-c:a", "aac", "-b:a", "192k",
        sliced_audio,
    ]
    res_a = _run_cmd(cmd_audio)
    if res_a.returncode != 0:
        raise RuntimeError(f"FFmpeg audio slice failed for {clip_id}: {res_a.stderr}")

    return SlicedClip(
        clip_id=clip_id,
        video_path=sliced_video,
        audio_path=sliced_audio,
        source_start_sec=start_sec,
        source_end_sec=end_sec,
        slice_start_sec=slice_start,
        relative_start_sec=relative_start,
        relative_end_sec=relative_end,
        target_duration_sec=target_duration,
        total_slice_duration_sec=slice_duration,
    )


async def slice_candidates(
    source_video: str,
    source_audio: str,
    candidates: list[dict],
    output_dir: str,
    pre_roll_sec: float = 1.5,
    post_roll_sec: float = 1.0,
) -> list[SlicedClip]:
    """
    Asynchronously extracts all candidate clips in parallel/sequential batches
    without blocking the FastAPI event loop.
    """
    loop = asyncio.get_running_loop()
    sliced_clips: list[SlicedClip] = []

    for c in candidates:
        clip_id = str(c.get("clip_id", "clip_1"))
        start_sec = float(c.get("start_sec", 0.0))
        end_sec = float(c.get("end_sec", 0.0))

        if end_sec <= start_sec:
            logger.warning("Skipping invalid clip interval [%.2f - %.2f] for %s", start_sec, end_sec, clip_id)
            continue

        clip = await loop.run_in_executor(
            None,
            slice_clip_sync,
            source_video,
            source_audio,
            clip_id,
            start_sec,
            end_sec,
            output_dir,
            pre_roll_sec,
            post_roll_sec,
        )
        sliced_clips.append(clip)

    logger.info("Successfully sliced %d candidate clips into %s", len(sliced_clips), output_dir)
    return sliced_clips
