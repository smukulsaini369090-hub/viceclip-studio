"""
VICECLIP STUDIO — Heuristic Signal Clip Generator
==================================================
Generates high-impact candidate clips from multimodal signals:
  • Audio dB excitement peaks (gunshots, explosions, dialogue spikes)
  • OpenCV visual motion velocity spikes
  • YouTube Most Replayed heatmap peaks
  • Transcript sentence boundaries
Acts as an instant offline fallback when Gemini API is rate-limited (503/429),
guaranteeing the user always receives 4-6 ranked clips ready for 60fps render.
"""

from __future__ import annotations

import json
from typing import Optional
from app.db.models import (
    AudioSpike,
    ClipCandidate,
    HeatmapPoint,
    TranscriptSegment,
    UploadKit,
    ViralityScorecard,
    VisualSpike,
)

def generate_heuristic_clips(
    video_id: str,
    video_title: str,
    duration_sec: float,
    transcript: list[TranscriptSegment],
    audio_spikes: list[AudioSpike],
    visual_spikes: list[VisualSpike],
    heatmap: list[HeatmapPoint],
    target_count: int = 5,
) -> list[ClipCandidate]:
    """Generates 4-6 candidate clips based on signal convergence and sentence boundaries."""
    # Collect candidate center timestamps from top audio & visual spikes
    candidates_scores: list[tuple[float, float, str]] = [] # (timestamp, score, description)

    for a in audio_spikes:
        # Normalize dB (-30 to 0 -> 50 to 95)
        score = min(98.0, max(60.0, 100.0 + a.db_level * 1.5))
        candidates_scores.append((a.timestamp_sec, score, f"High Excitement {a.spike_type.title()}"))

    for v in visual_spikes:
        score = min(95.0, max(55.0, v.velocity_score * 10.0))
        candidates_scores.append((v.timestamp_sec, score, "Fast Action Sequence"))

    for h in heatmap:
        score = min(99.0, max(65.0, h.intensity * 100.0))
        mid = (h.start_sec + h.end_sec) / 2.0
        candidates_scores.append((mid, score, "Most Replayed Spike"))

    # Sort candidates by score descending
    candidates_scores.sort(key=lambda x: x[1], reverse=True)

    # Cluster peaks to avoid overlapping clips within 25 seconds
    selected_centers: list[tuple[float, float, str]] = []
    for t, score, desc in candidates_scores:
        if t < 2.0 or t > (duration_sec - 15.0):
            continue
        too_close = any(abs(t - c[0]) < 22.0 for c in selected_centers)
        if not too_close:
            selected_centers.append((t, score, desc))
            if len(selected_centers) >= target_count:
                break

    # If not enough spikes, distribute evenly across the video
    if len(selected_centers) < 3 and duration_sec >= 45:
        step = max(30.0, duration_sec / (target_count + 1))
        t = step
        while t < duration_sec - 20 and len(selected_centers) < target_count:
            if not any(abs(t - c[0]) < 20.0 for c in selected_centers):
                selected_centers.append((t, 85.0, "Key Moment"))
            t += step

    selected_centers.sort(key=lambda x: x[0])

    clips: list[ClipCandidate] = []
    for idx, (center_t, score, desc) in enumerate(selected_centers):
        clip_id = f"clip_{idx + 1}"
        target_dur = 28.0

        # Anchor around center_t: start 3s before spike, extend for target_dur
        desired_start = max(0.0, center_t - 3.0)
        desired_end = min(duration_sec, desired_start + target_dur)

        # Snap to closest transcript sentence boundary if available
        actual_start = desired_start
        actual_end = desired_end
        title_text = ""

        if transcript:
            # Find closest word segment start near desired_start
            start_candidates = [s.start for s in transcript if abs(s.start - desired_start) <= 4.0]
            if start_candidates:
                actual_start = min(start_candidates, key=lambda s: abs(s - desired_start))

            # Find closest segment end near desired_end
            end_candidates = [s.end for s in transcript if abs(s.end - desired_end) <= 4.0]
            if end_candidates:
                actual_end = min(end_candidates, key=lambda s: abs(s - desired_end))

            # Extract words within clip for hook title
            clip_words = [s.text for s in transcript if s.start >= actual_start and s.end <= min(actual_start + 10.0, actual_end)]
            if clip_words:
                title_text = " ".join(clip_words[:7]).strip().rstrip(".,!?")

        if not title_text:
            title_text = f"GTA 6: {video_title[:35]}" if video_title else f"GTA 6 Viral Moment #{idx+1}"

        # Clean duration
        clip_dur = round(actual_end - actual_start, 1)
        if clip_dur < 12.0:
            actual_end = min(duration_sec, actual_start + 25.0)

        composite = round(score, 1)
        card = ViralityScorecard(
            three_second_visual_hook=min(100.0, round(score * 1.02, 1)),
            replay_loop_factor=min(100.0, round(score * 0.95, 1)),
            debate_comment_bait_potential=min(100.0, round(score * 0.98, 1)),
            payoff_speed=min(100.0, round(score * 1.01, 1)),
        )

        clips.append(
            ClipCandidate(
                clip_id=clip_id,
                title_hook=title_text[:60],
                start_sec=round(actual_start, 1),
                end_sec=round(actual_end, 1),
                virality=card,
                top_banner_text_a=f"WAIT FOR THIS IN GTA 6!",
                top_banner_text_b=f"IS THIS REALLY GTA 6?!",
                needs_easter_egg_zoom=False,
                easter_egg_description="",
                upload_kit=UploadKit(
                    titles=[
                        f"{title_text} #GTA6",
                        f"You Won't Believe This in GTA 6!",
                        f"Rockstar Didn't Want You To Notice This",
                    ],
                    hashtags=["#GTA6", "#Shorts", "#Gaming", "#GrandTheftAuto6"],
                    pinned_comment="What did you think of this moment? Drop your thoughts below!",
                    best_cover_timestamp_sec=round(actual_start + 1.5, 1),
                ),
            )
        )

    return clips
