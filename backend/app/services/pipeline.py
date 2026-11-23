"""
VICECLIP STUDIO — Full Pipeline Orchestrator
==============================================
Coordinates Pass 1 through Pass 4 operations with real-time SSE telemetry:
  1. Smart Cache check (instant reload by YouTube Video ID).
  2. Pass 1: Extraction, Whisper CUDA transcription, Librosa/OpenCV signal spikes.
  3. Pass 2: GTA 6 Lore & Retention Vault prompt assembly -> Gemini Brain (API or Manual mode).
  4. Pass 3: Lossless keyframe-safe clip isolation (pre-roll buffer).
  5. Pass 4: VRAM-safe sequential GPU stages:
     - Copyright Music Shield (Demucs) + SFX/music bed
     - Transformative commentary voiceover (edge-tts)
     - Silence dead-air removal (FFmpeg silencedetect)
     - Smart gaming framing (MediaPipe split-screen or 9:16 crop)
     - God-Mode Easter-egg zoom (Gemini Vision)
     - GPU render (NVENC) + Dual-Hook A/B export + Shorts cover PNG
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Callable, Coroutine, Optional

from app.config import get_settings
from app.core.audio_shield import mix_soundtrack_and_sfx, process_copyright_shield
from app.core.commentary_engine import generate_transformative_commentary
from app.core.dead_air import process_dead_air
from app.core.framing_engine import analyze_framing
from app.core.gemini_brain import get_manual_prompt, run_viral_brain_api
from app.core.nvenc_renderer import export_clip_with_dual_hook
from app.core.signal_analyzer import analyse_signals
from app.core.slicer import slice_clip_sync
from app.core.transcriber import transcribe_audio
from app.core.vision_zoom import detect_easter_egg_coordinates
from app.core.vram_manager import get_vram_manager
from app.core.yt_extractor import extract_video, normalize_video_id
from app.db.database import (
    cache_get_video,
    cache_upsert_video,
    clips_get_by_video,
    clips_save_candidates,
    clips_update_status,
    vault_get_top_winners,
)
from app.db.models import (
    AudioSpike,
    ClipCandidate,
    CropOverride,
    HeatmapPoint,
    RenderSettings,
    TimestampedComment,
    TranscriptSegment,
    TrimAdjustment,
    ViralBrainResponse,
    VisualSpike,
)

logger = logging.getLogger("viceclip.pipeline")

TelemetryCallback = Optional[Callable[[dict], Coroutine[None, None, None]]]


async def _emit(telemetry_cb: TelemetryCallback, stage: str, label: str, progress: float, msg: str, **kwargs) -> None:
    """Helper to dispatch telemetry event."""
    if telemetry_cb:
        mgr = get_vram_manager()
        v_stat = mgr.get_vram_status()
        payload = {
            "stage": stage,
            "stage_label": label,
            "progress_pct": progress,
            "log_message": msg,
            "vram_used_mb": v_stat["used_mb"],
            "vram_total_mb": v_stat["total_mb"],
            "vram_pct": v_stat["utilization_pct"],
            **kwargs,
        }
        await telemetry_cb(payload)


# ═══════════════════════════════════════════════════════════════════════════════
# PASS 1 & PASS 2: ANALYZE VIDEO
# ═══════════════════════════════════════════════════════════════════════════════

async def run_analysis_pipeline(
    url: str,
    settings: Optional[RenderSettings] = None,
    telemetry_cb: TelemetryCallback = None,
) -> dict:
    """
    Executes Pass 1 & Pass 2 analysis:
      - Checks SQLite Smart Cache first.
      - If uncached: downloads, transcribes, analyzes audio/visual signals, and queries Gemini.
      - Returns analysis results, candidate clips, and manual prompt if manual mode is enabled.
    """
    cfg = get_settings()
    opts = settings or RenderSettings()
    video_id = normalize_video_id(url)

    await _emit(telemetry_cb, "smart_cache", "Checking Smart Cache", 5.0, f"Checking cache for video ID: {video_id}")

    cached = await cache_get_video(video_id)
    if cached and cached.get("transcript_json") != "[]":
        logger.info("Found video %s in SQLite Smart Cache! Loading instantly.", video_id)
        await _emit(telemetry_cb, "smart_cache", "Smart Cache Hit", 100.0, "Loaded video intelligence from cache.")

        existing_clips = await clips_get_by_video(video_id)
        manual_prompt = None

        raw_t = json.loads(cached.get("transcript_json", "[]"))
        transcript = [TranscriptSegment(**s) for s in raw_t]
        raw_hm = json.loads(cached.get("heatmap_json", "[]"))
        heatmap = [HeatmapPoint(**h) for h in raw_hm]
        raw_c = json.loads(cached.get("comments_json", "[]"))
        comments = [TimestampedComment(**c) for c in raw_c]
        raw_a = json.loads(cached.get("audio_spikes_json", "[]"))
        audio_spikes = [AudioSpike(**a) for a in raw_a]
        raw_v = json.loads(cached.get("visual_spikes_json", "[]"))
        visual_spikes = [VisualSpike(**v) for v in raw_v]
        top_winners = await vault_get_top_winners(limit=5)

        if opts.manual_gemini_mode:
            manual_prompt = get_manual_prompt(
                video_title=cached.get("title", ""),
                video_channel=cached.get("channel", ""),
                video_duration_sec=cached.get("duration_sec", 0),
                transcript_segments=transcript,
                heatmap=heatmap,
                comments=comments,
                audio_spikes=audio_spikes,
                visual_spikes=visual_spikes,
                retention_vault_winners=top_winners,
            )
        elif not existing_clips:
            try:
                await _emit(telemetry_cb, "viral_brain", "Gemini Viral Reasoning", 80.0, "Scoring viral hooks and detecting Easter eggs via Gemini API...")
                brain_response = await run_viral_brain_api(
                    video_title=cached.get("title", ""),
                    video_channel=cached.get("channel", ""),
                    video_duration_sec=cached.get("duration_sec", 0),
                    transcript_segments=transcript,
                    heatmap=heatmap,
                    comments=comments,
                    audio_spikes=audio_spikes,
                    visual_spikes=visual_spikes,
                    retention_vault_winners=top_winners,
                )
                clips_dicts = [c.model_dump() for c in brain_response.clips]
                await clips_save_candidates(video_id, clips_dicts)
                existing_clips = await clips_get_by_video(video_id)
            except Exception as exc:
                logger.error("Gemini API call failed for cached video: %s. Using heuristic signal fallback & generating manual prompt.", exc)
                from app.core.heuristic_clips import generate_heuristic_clips
                heuristic_candidates = generate_heuristic_clips(
                    video_id=video_id,
                    video_title=cached.get("title", ""),
                    duration_sec=cached.get("duration_sec", 0),
                    transcript=transcript,
                    audio_spikes=audio_spikes,
                    visual_spikes=visual_spikes,
                    heatmap=heatmap,
                )
                clips_dicts = [c.model_dump() for c in heuristic_candidates]
                await clips_save_candidates(video_id, clips_dicts)
                existing_clips = await clips_get_by_video(video_id)
                manual_prompt = get_manual_prompt(
                    video_title=cached.get("title", ""),
                    video_channel=cached.get("channel", ""),
                    video_duration_sec=cached.get("duration_sec", 0),
                    transcript_segments=transcript,
                    heatmap=heatmap,
                    comments=comments,
                    audio_spikes=audio_spikes,
                    visual_spikes=visual_spikes,
                    retention_vault_winners=top_winners,
                )

        return {
            "cached": True,
            "video_id": video_id,
            "title": cached.get("title", ""),
            "channel": cached.get("channel", ""),
            "duration_sec": cached.get("duration_sec", 0),
            "thumbnail_url": cached.get("thumbnail_url", ""),
            "download_path": cached.get("download_path", ""),
            "audio_path": cached.get("audio_path", ""),
            "clips": existing_clips,
            "manual_prompt": manual_prompt,
        }

    # 1. Download Video & Extract Metadata
    await _emit(telemetry_cb, "extracting", "Downloading Media", 15.0, f"Extracting video streams & comments via yt-dlp...")
    extraction = await extract_video(url)

    # 2. CUDA Whisper Transcription
    await _emit(telemetry_cb, "whisper_gpu", "Whisper CUDA Transcription", 35.0, "Running word-level transcription on GPU...")
    transcript = await transcribe_audio(extraction.audio_path)

    # 3. Excitement Spikes (Librosa + OpenCV)
    await _emit(telemetry_cb, "signals", "Analyzing Action Signals", 55.0, "Detecting audio dB peaks and visual velocity spikes...")
    audio_spikes, visual_spikes = await analyse_signals(extraction.video_path, extraction.audio_path)

    # Save initial intelligence to SQLite Smart Cache
    cache_entry = extraction.to_cache_dict()
    cache_entry["transcript_json"] = [s.model_dump() if hasattr(s, "model_dump") else s for s in transcript]
    cache_entry["audio_spikes_json"] = [s.model_dump() if hasattr(s, "model_dump") else s for s in audio_spikes]
    cache_entry["visual_spikes_json"] = [s.model_dump() if hasattr(s, "model_dump") else s for s in visual_spikes]
    await cache_upsert_video(video_id, cache_entry)

    # 4. Fetch Retention Vault Winners for prompt injection
    top_winners = await vault_get_top_winners(limit=5)

    # 5. Pass 2: Gemini Viral Brain
    manual_prompt = None
    clips_list: list[dict] = []

    if opts.manual_gemini_mode:
        await _emit(telemetry_cb, "manual_gemini", "Manual Web Mode Active", 90.0, "Compiled analysis prompt for gemini.google.com")
        manual_prompt = get_manual_prompt(
            video_title=extraction.title,
            video_channel=extraction.channel,
            video_duration_sec=extraction.duration_sec,
            transcript_segments=transcript,
            heatmap=extraction.heatmap,
            comments=extraction.comments,
            audio_spikes=audio_spikes,
            visual_spikes=visual_spikes,
            retention_vault_winners=top_winners,
        )
    else:
        await _emit(telemetry_cb, "viral_brain", "Gemini Viral Reasoning", 80.0, "Scoring viral hooks and detecting Easter eggs via Gemini API...")
        try:
            brain_response = await run_viral_brain_api(
                video_title=extraction.title,
                video_channel=extraction.channel,
                video_duration_sec=extraction.duration_sec,
                transcript_segments=transcript,
                heatmap=extraction.heatmap,
                comments=extraction.comments,
                audio_spikes=audio_spikes,
                visual_spikes=visual_spikes,
                retention_vault_winners=top_winners,
            )
            clips_dicts = [c.model_dump() for c in brain_response.clips]
            await clips_save_candidates(video_id, clips_dicts)
            clips_list = await clips_get_by_video(video_id)
        except Exception as exc:
            logger.error("Gemini API call failed: %s. Using heuristic signal fallback & generating manual prompt.", exc)
            from app.core.heuristic_clips import generate_heuristic_clips
            heuristic_candidates = generate_heuristic_clips(
                video_id=video_id,
                video_title=extraction.title,
                duration_sec=extraction.duration_sec,
                transcript=transcript,
                audio_spikes=audio_spikes,
                visual_spikes=visual_spikes,
                heatmap=extraction.heatmap,
            )
            clips_dicts = [c.model_dump() for c in heuristic_candidates]
            await clips_save_candidates(video_id, clips_dicts)
            clips_list = await clips_get_by_video(video_id)
            manual_prompt = get_manual_prompt(
                video_title=extraction.title,
                video_channel=extraction.channel,
                video_duration_sec=extraction.duration_sec,
                transcript_segments=transcript,
                heatmap=extraction.heatmap,
                comments=extraction.comments,
                audio_spikes=audio_spikes,
                visual_spikes=visual_spikes,
                retention_vault_winners=top_winners,
            )

    await _emit(telemetry_cb, "complete", "Analysis Complete", 100.0, f"Analysis ready: {len(clips_list)} candidate clips found.")

    return {
        "cached": False,
        "video_id": video_id,
        "title": extraction.title,
        "channel": extraction.channel,
        "duration_sec": extraction.duration_sec,
        "thumbnail_url": extraction.thumbnail_url,
        "download_path": extraction.video_path,
        "audio_path": extraction.audio_path,
        "clips": clips_list,
        "manual_prompt": manual_prompt,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PASS 3 & PASS 4: RENDER CLIP
# ═══════════════════════════════════════════════════════════════════════════════

async def run_render_pipeline(
    video_id: str,
    clip_id: str,
    settings: Optional[RenderSettings] = None,
    custom_crop: Optional[CropOverride] = None,
    trim: Optional[TrimAdjustment] = None,
    telemetry_cb: TelemetryCallback = None,
) -> dict:
    """
    Executes Pass 3 & Pass 4 render pipeline for a single selected candidate clip:
      - Keyframe slice with pre-roll.
      - Optional Demucs stem stripping + SFX mix.
      - Optional Transformative Commentary voiceover.
      - Optional silence dead-air trimming.
      - Smart gaming framing (facecam/gameplay).
      - Optional Easter-egg auto-zoom callout.
      - NVENC GPU export (Variant A & Variant B) + Shorts cover frame.
    """
    cfg = get_settings()
    opts = settings or RenderSettings()

    cached = await cache_get_video(video_id)
    if not cached:
        raise ValueError(f"Video {video_id} not found in cache. Analyze it first.")

    clips = await clips_get_by_video(video_id)
    target_clip = next((c for c in clips if c["clip_id"] == clip_id), None)
    if not target_clip:
        raise ValueError(f"Clip {clip_id} not found for video {video_id}")

    # Determine timing
    start_sec = trim.start_sec if trim else target_clip["start_sec"]
    end_sec = trim.end_sec if trim else target_clip["end_sec"]
    clip_db_id = target_clip["id"]

    clip_out_dir = Path(cfg.output_dir) / "clips" / video_id
    clip_out_dir.mkdir(parents=True, exist_ok=True)

    await clips_update_status(clip_db_id, "rendering")

    # 1. Pass 3: Lossless Slice with 1.5s Pre-Roll
    await _emit(telemetry_cb, "lossless_slice", "Lossless Keyframe Slicing", 10.0, f"Extracting clip interval [{start_sec:.1f}s - {end_sec:.1f}s] with pre-roll buffer...")
    slice_data = slice_clip_sync(
        source_video=cached["download_path"],
        source_audio=cached["audio_path"],
        clip_id=clip_id,
        start_sec=start_sec,
        end_sec=end_sec,
        output_dir=str(clip_out_dir),
        pre_roll_sec=1.5,
        post_roll_sec=1.0,
    )

    current_video = slice_data.video_path
    current_audio = slice_data.audio_path
    current_rel_start = slice_data.relative_start_sec
    current_duration = slice_data.target_duration_sec

    # Parse word segments for this clip
    raw_transcript = json.loads(cached.get("transcript_json", "[]"))
    clip_segments = [
        TranscriptSegment(**s) for s in raw_transcript
        if s.get("start", 0) >= (start_sec - 0.5) and s.get("end", 0) <= (end_sec + 0.5)
    ]
    # Re-normalize segment timestamps relative to clip start (t=0 at actual clip start)
    rel_segments = [
        TranscriptSegment(
            text=s.text,
            start=max(0.0, s.start - start_sec),
            end=max(0.1, s.end - start_sec),
            confidence=s.confidence,
        )
        for s in clip_segments
    ]

    # 2. Stage A: Copyright Shield (Demucs) + SFX
    if opts.enable_demucs:
        await _emit(telemetry_cb, "demucs_gpu", "Demucs Stem Separation", 25.0, "Isolating speech/SFX and muting copyrighted radio stems...")
        clean_speech = await process_copyright_shield(current_audio, str(clip_out_dir))
        mixed_audio = str(clip_out_dir / f"{clip_id}_shielded.m4a")
        mix_soundtrack_and_sfx(
            primary_audio_path=clean_speech,
            output_mixed_path=mixed_audio,
            target_duration_sec=slice_data.total_slice_duration_sec,
            enable_music_bed=True,
            add_hook_whoosh=True,
            add_bass_impact=True,
        )
        current_audio = mixed_audio
    else:
        # Subtle SFX layering directly on original audio
        mixed_audio = str(clip_out_dir / f"{clip_id}_sfx_mixed.m4a")
        mix_soundtrack_and_sfx(
            primary_audio_path=current_audio,
            output_mixed_path=mixed_audio,
            target_duration_sec=slice_data.total_slice_duration_sec,
            enable_music_bed=False,
            add_hook_whoosh=True,
            add_bass_impact=True,
        )
        current_audio = mixed_audio

    # 3. Stage D: Transformative Commentary Voiceover (edge-tts)
    if opts.enable_commentary:
        await _emit(telemetry_cb, "commentary_tts", "Transformative Commentary", 45.0, "Synthesizing AI breakdown commentary via edge-tts...")
        full_clip_text = " ".join(s.text for s in clip_segments)
        commentary = await generate_transformative_commentary(
            clip_title=target_clip.get("title_hook", ""),
            clip_transcript=full_clip_text,
            clip_duration_sec=current_duration,
            video_title=cached.get("title", ""),
            gameplay_audio_path=current_audio,
            output_dir=str(clip_out_dir),
            clip_id=clip_id,
            voice=opts.commentary_voice,
        )
        current_audio = commentary.mixed_audio_path
        if commentary.segments:
            rel_segments = commentary.segments

    # 4. Stage E: Dead-Air Silence Removal
    if opts.enable_dead_air_cut:
        await _emit(telemetry_cb, "dead_air", "Auto Dead-Air Trimmer", 60.0, "Removing pauses >0.4s and applying smooth crossfades...")
        cut_v, cut_a, new_dur = await process_dead_air(
            input_video=current_video,
            input_audio=current_audio,
            output_dir=str(clip_out_dir),
            clip_id=clip_id,
            total_duration=slice_data.total_slice_duration_sec,
            min_silence_duration=0.40,
        )
        current_video = cut_v
        current_audio = cut_a

    # 5. Stage B: Smart Gaming Framing (MediaPipe)
    await _emit(telemetry_cb, "mediapipe_gpu", "Smart Gaming Framing", 75.0, "Computing Facecam/Gameplay 9:16 layout split...")
    framing = await analyze_framing(
        video_path=current_video,
        custom_crop=custom_crop,
        allow_split_screen=True,
    )

    # 6. Stage C: God-Mode Easter-Egg Auto-Zoom
    needs_zoom = bool(target_clip.get("needs_easter_egg_zoom", 0)) and opts.enable_easter_egg_zoom
    if needs_zoom:
        await _emit(telemetry_cb, "vision_zoom", "Easter-Egg Auto-Zoom", 85.0, "Detecting Easter egg coordinates with Gemini Vision...")
        egg_desc = target_clip.get("easter_egg_description", "GTA 6 hidden detail")
        # Extract sample keyframe at relative midpoint
        from app.core.vision_zoom import extract_keyframe_sync
        kf_path = str(clip_out_dir / f"{clip_id}_keyframe.png")
        try:
            extract_keyframe_sync(current_video, current_rel_start + 2.0, kf_path)
            await detect_easter_egg_coordinates(kf_path, egg_desc, zoom_start_sec=1.5)
        except Exception as exc:
            logger.warning("Easter egg coordinate detection skipped: %s", exc)

    # 7. Stage E: NVENC GPU Render & Dual-Hook A/B Export
    await _emit(telemetry_cb, "nvenc_render", "NVENC GPU 60fps Render", 90.0, "Encoding 1080x1920 MP4 via h264_nvenc with animated ASS subtitles...")

    banner_a = target_clip.get("banner_text_a") or target_clip.get("top_banner_text_a") or ""
    banner_b = target_clip.get("banner_text_b") or target_clip.get("top_banner_text_b") or ""

    upload_kit_data = json.loads(target_clip.get("upload_kit_json", "{}"))
    best_cover_time = upload_kit_data.get("best_cover_timestamp_sec", 1.5)

    render_result = await export_clip_with_dual_hook(
        clip_id=clip_id,
        input_video_path=current_video,
        input_audio_path=current_audio,
        framing_filter_str=framing.ffmpeg_filter,
        relative_start_sec=current_rel_start,
        clip_duration_sec=current_duration,
        segments=rel_segments,
        output_dir=str(clip_out_dir),
        top_banner_text_a=banner_a,
        top_banner_text_b=banner_b,
        caption_theme=opts.caption_theme,
        enable_dual_hook=opts.enable_dual_hook,
        best_cover_sec=best_cover_time,
    )

    # Update database
    await clips_update_status(
        clip_db_id=clip_db_id,
        status="completed",
        output_a=render_result.variant_a_path,
        output_b=render_result.variant_b_path or "",
        cover=render_result.cover_image_path,
    )

    await _emit(telemetry_cb, "complete", "Clip Exported Successfully", 100.0, f"Render finished: {Path(render_result.variant_a_path).name}")

    return {
        "clip_id": clip_id,
        "status": "completed",
        "variant_a_path": render_result.variant_a_path,
        "variant_b_path": render_result.variant_b_path,
        "cover_image_path": render_result.cover_image_path,
        "duration_sec": render_result.duration_sec,
        "encoder_used": render_result.encoder_used,
    }
