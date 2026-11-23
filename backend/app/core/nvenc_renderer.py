"""
VICECLIP STUDIO — NVENC GPU Renderer & Dual-Hook A/B Exporter  (Pass 4 Stage E)
==================================================================================
Hardware-accelerated rendering pipeline engineered specifically for RTX 3050 (6 GB VRAM):
  1. NVIDIA `h264_nvenc` GPU encoding (1080x1920 @ 60fps, `-preset p4 -rc vbr -cq 19 -b:v 10M`).
  2. Safe Windows path escaping for FFmpeg `ass` filter (`ass='C\\:/...'` format).
  3. Automatic CPU fallback to `libx264` if NVENC sessions are exhausted or unsupported.
  4. Dual-Hook A/B Export: Automatically renders Variant A and Variant B with different
     curiosity hook banners for the #1 ranked clip.
  5. Shorts Cover Frame: Extracts high-contrast 1080x1920 thumbnail PNG at optimal timestamp.
  6. GPU lock orchestration via `VRAMManager.acquire_gpu(GPUStage.NVENC_RENDER)`.
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
from app.core.ass_captions import generate_ass_file
from app.core.vram_manager import GPUStage, flush_gpu_memory, get_vram_manager
from app.db.models import TranscriptSegment

logger = logging.getLogger("viceclip.renderer")

_WIN_CREATE_NO_WINDOW: int = 0x08000000 if sys.platform == "win32" else 0


@dataclass
class RenderOutput:
    """Paths to rendered assets."""
    clip_id: str
    variant_a_path: str
    variant_b_path: Optional[str]
    cover_image_path: str
    duration_sec: float
    encoder_used: str


def _run_cmd(cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    """Run subprocess silently on Windows."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=_WIN_CREATE_NO_WINDOW,
    )


def extract_cover_thumbnail_sync(
    video_path: str,
    output_png_path: str,
    timestamp_sec: float = 1.5,
) -> str:
    """Extracts a sharp 1080x1920 cover image for YouTube Shorts."""
    settings = get_settings()
    out_file = Path(output_png_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        settings.ffmpeg_path, "-y", "-loglevel", "error",
        "-ss", f"{timestamp_sec:.3f}",
        "-i", str(Path(video_path).resolve()),
        "-frames:v", "1",
        "-q:v", "2",
        str(out_file),
    ]

    res = _run_cmd(cmd, timeout=30)
    if res.returncode != 0 or not out_file.is_file():
        logger.warning("Cover extraction failed: %s. Retrying at t=0.5s...", res.stderr)
        cmd[3] = "0.500"
        _run_cmd(cmd, timeout=30)

    return str(out_file)


def render_short_sync(
    input_video_path: str,
    input_audio_path: str,
    ass_subtitles_path: str,
    output_mp4_path: str,
    framing_filter_str: str,
    relative_start_sec: float,
    clip_duration_sec: float,
    encoder_name: str = "h264_nvenc",
    target_fps: int = 60,
) -> tuple[str, str]:
    """
    Renders a single 1080x1920 @ 60fps MP4 using FFmpeg.
    Returns: (output_path, actual_encoder_used)
    """
    settings = get_settings()
    ffmpeg_bin = settings.ffmpeg_path

    out_file = Path(output_mp4_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Windows-safe path escaping for ASS subtitles filter:
    # Example: 'C\:/Users/mukul/Downloads/ViceClip-Studio/...'
    safe_ass_arg = settings.ffmpeg_ass_path(ass_subtitles_path)

    # Composite video filter chain:
    # [0:v] Framing Layout -> [framed_v] -> Trim relative pre-roll -> Burn ASS subtitles -> [vout]
    # Note: relative_start_sec cuts off the 1.5s pre-roll cleanly on an exact frame!
    filter_complex = (
        f"{framing_filter_str};"
        f"[framed_v]trim=start={relative_start_sec:.3f}:duration={clip_duration_sec:.3f},"
        f"setpts=PTS-STARTPTS,"
        f"ass={safe_ass_arg}[vout]"
    )

    # Audio filter chain: trim audio to exact clip bounds
    audio_filter = f"atrim=start={relative_start_sec:.3f}:duration={clip_duration_sec:.3f},asetpts=PTS-STARTPTS"

    # Configure video encoder flags
    actual_encoder = encoder_name
    if encoder_name == "h264_nvenc":
        encoder_args = [
            "-c:v", "h264_nvenc",
            "-preset", settings.nvenc_preset,
            "-rc", "vbr",
            "-cq", str(settings.nvenc_cq),
            "-b:v", settings.nvenc_bitrate,
            "-pix_fmt", "yuv420p",
            "-r", str(target_fps),
        ]
    else:
        encoder_args = [
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "19",
            "-pix_fmt", "yuv420p",
            "-r", str(target_fps),
        ]

    cmd = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-i", str(Path(input_video_path).resolve()),
        "-i", str(Path(input_audio_path).resolve()),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "1:a",
        "-af", audio_filter,
        *encoder_args,
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_file),
    ]

    logger.info("Executing GPU encode (%s) -> %s", actual_encoder, out_file.name)
    res = _run_cmd(cmd, timeout=360)

    # Automatic fallback to libx264 if NVENC fails
    if res.returncode != 0:
        if actual_encoder == "h264_nvenc":
            logger.warning("h264_nvenc failed (%d): %s. Falling back to CPU libx264...", res.returncode, res.stderr)
            actual_encoder = "libx264"
            cmd_fallback = [
                ffmpeg_bin, "-y", "-loglevel", "error",
                "-i", str(Path(input_video_path).resolve()),
                "-i", str(Path(input_audio_path).resolve()),
                "-filter_complex", filter_complex,
                "-map", "[vout]",
                "-map", "1:a",
                "-af", audio_filter,
                "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-pix_fmt", "yuv420p", "-r", str(target_fps),
                "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart",
                str(out_file),
            ]
            res_fb = _run_cmd(cmd_fallback, timeout=480)
            if res_fb.returncode != 0:
                raise RuntimeError(f"FFmpeg render failed with both NVENC and libx264: {res_fb.stderr}")
        else:
            raise RuntimeError(f"FFmpeg render failed: {res.stderr}")

    logger.info("Render complete: %s (%.1f MB, encoder=%s)", out_file.name, out_file.stat().st_size / (1024 * 1024), actual_encoder)
    return str(out_file), actual_encoder


async def export_clip_with_dual_hook(
    clip_id: str,
    input_video_path: str,
    input_audio_path: str,
    framing_filter_str: str,
    relative_start_sec: float,
    clip_duration_sec: float,
    segments: list[TranscriptSegment],
    output_dir: str,
    top_banner_text_a: str,
    top_banner_text_b: str = "",
    caption_theme: str = "vice_city_neon",
    enable_dual_hook: bool = True,
    best_cover_sec: float = 1.5,
) -> RenderOutput:
    """
    Renders Variant A, optional Variant B (for Dual-Hook A/B testing),
    and the high-contrast Shorts cover thumbnail PNG.
    """
    settings = get_settings()
    mgr = get_vram_manager()

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    variant_a_mp4 = str(out_dir / f"{clip_id}_variant_A.mp4")
    variant_b_mp4 = str(out_dir / f"{clip_id}_variant_B.mp4") if (enable_dual_hook and top_banner_text_b) else None
    cover_png = str(out_dir / f"{clip_id}_cover.png")

    # Generate ASS subtitle files
    ass_a = generate_ass_file(
        segments=segments,
        output_ass_path=str(out_dir / f"{clip_id}_subs_a.ass"),
        top_banner_text=top_banner_text_a,
        theme_name=caption_theme,
    )

    ass_b: Optional[str] = None
    if variant_b_mp4:
        ass_b = generate_ass_file(
            segments=segments,
            output_ass_path=str(out_dir / f"{clip_id}_subs_b.ass"),
            top_banner_text=top_banner_text_b,
            theme_name=caption_theme,
        )

    encoder_choice = settings.encoder  # h264_nvenc if supported, else libx264
    final_encoder = encoder_choice

    async with mgr.acquire_gpu(GPUStage.NVENC_RENDER):
        loop = asyncio.get_running_loop()

        # Render Variant A
        _, final_encoder = await loop.run_in_executor(
            None,
            render_short_sync,
            input_video_path,
            input_audio_path,
            ass_a,
            variant_a_mp4,
            framing_filter_str,
            relative_start_sec,
            clip_duration_sec,
            encoder_choice,
            settings.target_fps,
        )

        # Render Variant B if enabled
        if variant_b_mp4 and ass_b:
            await loop.run_in_executor(
                None,
                render_short_sync,
                input_video_path,
                input_audio_path,
                ass_b,
                variant_b_mp4,
                framing_filter_str,
                relative_start_sec,
                clip_duration_sec,
                final_encoder,
                settings.target_fps,
            )

        # Extract Cover PNG from Variant A
        await loop.run_in_executor(
            None,
            extract_cover_thumbnail_sync,
            variant_a_mp4,
            cover_png,
            min(best_cover_sec, clip_duration_sec - 0.5),
        )

        flush_gpu_memory()

    return RenderOutput(
        clip_id=clip_id,
        variant_a_path=variant_a_mp4,
        variant_b_path=variant_b_mp4,
        cover_image_path=cover_png,
        duration_sec=clip_duration_sec,
        encoder_used=final_encoder,
    )
