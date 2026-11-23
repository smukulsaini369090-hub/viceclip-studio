"""
VICECLIP STUDIO — Prompt Builder  (Pass 2)
============================================
Assembles the structured Gemini prompt from all Pass-1 intelligence:
  • Word-level transcript (timed blocks)
  • YouTube Most Replayed heatmap peaks
  • Timestamped fan comments
  • Audio dB spikes & visual velocity spikes
  • GTA 6 Lore Dictionary context
  • Retention Vault top-5 winning hook formulas

Outputs both the full prompt text **and** the strict JSON schema
definition so the Viral Brain returns Pydantic-valid data.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from app.core.gta6_lore import build_lore_context
from app.db.models import (
    AudioSpike,
    HeatmapPoint,
    TimestampedComment,
    TranscriptSegment,
    VisualSpike,
)

logger = logging.getLogger("viceclip.prompt")


# ═══════════════════════════════════════════════════════════════════════════════
# JSON OUTPUT SCHEMA (embedded in the prompt for strict adherence)
# ═══════════════════════════════════════════════════════════════════════════════

OUTPUT_JSON_SCHEMA: str = """\
{
  "clips": [
    {
      "clip_id": "clip_1",
      "title_hook": "string — punchy hook title (max 60 chars)",
      "start_sec": 0.0,
      "end_sec": 0.0,
      "virality": {
        "three_second_visual_hook": 0,
        "replay_loop_factor": 0,
        "debate_comment_bait_potential": 0,
        "payoff_speed": 0
      },
      "top_banner_text_a": "string — 3-second curiosity banner variant A (max 40 chars)",
      "top_banner_text_b": "string — 3-second curiosity banner variant B (max 40 chars)",
      "needs_easter_egg_zoom": false,
      "easter_egg_description": "string — what the hidden detail is (empty if no easter egg)",
      "upload_kit": {
        "titles": ["viral title 1", "viral title 2", "viral title 3"],
        "hashtags": ["#GTA6", "#ViceCity", "#Shorts"],
        "pinned_comment": "string — debate-sparking pinned comment",
        "best_cover_timestamp_sec": 0.0
      }
    }
  ],
  "analysis_summary": "string — brief analysis of the video's viral potential",
  "video_type": "gameplay|trailer|breakdown|review"
}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT ASSEMBLY
# ═══════════════════════════════════════════════════════════════════════════════


def _format_transcript_blocks(
    segments: list[TranscriptSegment],
    block_duration: float = 10.0,
) -> str:
    """Group word segments into timed blocks for the prompt."""
    if not segments:
        return "(No transcript available)"

    lines: list[str] = []
    block_start = segments[0].start
    block_words: list[str] = []

    for seg in segments:
        block_words.append(seg.text)
        if seg.end - block_start >= block_duration:
            lines.append(
                f"[{block_start:.1f}s – {seg.end:.1f}s] {' '.join(block_words)}"
            )
            block_start = seg.end
            block_words = []

    if block_words:
        lines.append(
            f"[{block_start:.1f}s – {segments[-1].end:.1f}s] {' '.join(block_words)}"
        )

    return "\n".join(lines)


def _format_heatmap(heatmap: list[HeatmapPoint], top_n: int = 10) -> str:
    """Format top heatmap peaks for the prompt."""
    if not heatmap:
        return "(No YouTube Most Replayed heatmap available for this video)"

    sorted_points = sorted(heatmap, key=lambda h: h.intensity, reverse=True)[:top_n]
    sorted_points.sort(key=lambda h: h.start_sec)

    lines: list[str] = []
    for hp in sorted_points:
        pct = int(hp.intensity * 100)
        lines.append(f"  [{hp.start_sec:.0f}s – {hp.end_sec:.0f}s] intensity={pct}%")
    return "\n".join(lines)


def _format_comments(comments: list[TimestampedComment], top_n: int = 15) -> str:
    """Format top timestamped fan comments for the prompt."""
    if not comments:
        return "(No timestamped comments available)"

    top = sorted(comments, key=lambda c: c.likes, reverse=True)[:top_n]
    lines: list[str] = []
    for tc in top:
        m, s = divmod(int(tc.timestamp_sec), 60)
        likes_str = f" ({tc.likes} likes)" if tc.likes > 0 else ""
        text_preview = tc.text[:120].replace("\n", " ")
        lines.append(f"  @{m}:{s:02d}{likes_str}: {text_preview}")
    return "\n".join(lines)


def _format_audio_spikes(spikes: list[AudioSpike], top_n: int = 15) -> str:
    """Format top audio excitement spikes for the prompt."""
    if not spikes:
        return "(No significant audio spikes detected)"

    top = sorted(spikes, key=lambda s: s.db_level, reverse=True)[:top_n]
    top.sort(key=lambda s: s.timestamp_sec)

    lines: list[str] = []
    for sp in top:
        m, s = divmod(int(sp.timestamp_sec), 60)
        lines.append(f"  @{m}:{s:02d} dB={sp.db_level:+.0f} type={sp.spike_type}")
    return "\n".join(lines)


def _format_visual_spikes(spikes: list[VisualSpike], top_n: int = 10) -> str:
    """Format top visual velocity spikes for the prompt."""
    if not spikes:
        return "(No significant visual action spikes detected)"

    top = sorted(spikes, key=lambda s: s.velocity_score, reverse=True)[:top_n]
    top.sort(key=lambda s: s.timestamp_sec)

    lines: list[str] = []
    for sp in top:
        m, s = divmod(int(sp.timestamp_sec), 60)
        lines.append(
            f"  @{m}:{s:02d} velocity={sp.velocity_score:.1f} ({sp.description})"
        )
    return "\n".join(lines)


def _format_retention_vault(winners: list[dict]) -> str:
    """Format Retention Vault top-5 winners for self-learning injection."""
    if not winners:
        return "(No previous performance data yet — this is the first run)"

    lines: list[str] = []
    for i, w in enumerate(winners, 1):
        lines.append(
            f"  #{i}: \"{w.get('title_hook', '')}\" — "
            f"AVD={w.get('avd_pct', 0):.0f}%, "
            f"Views={w.get('views_48h', 0):,}, "
            f"Hook=\"{w.get('hook_formula', '')}\", "
            f"Pattern=\"{w.get('clip_pattern', '')}\""
        )
    return "\n".join(lines)


def build_viral_brain_prompt(
    *,
    video_title: str,
    video_channel: str,
    video_duration_sec: float,
    transcript_segments: list[TranscriptSegment],
    heatmap: list[HeatmapPoint],
    comments: list[TimestampedComment],
    audio_spikes: list[AudioSpike],
    visual_spikes: list[VisualSpike],
    retention_vault_winners: list[dict],
    video_type_hint: str = "auto",
) -> str:
    """
    Build the complete Gemini Viral Brain prompt.

    This prompt is used identically for:
      1. **API mode** — sent directly to the Gemini SDK.
      2. **Manual Copy-Paste Web mode** — displayed for the user to copy
         and paste into ``gemini.google.com``.

    Returns
    -------
    str
        The full prompt text with all context and the JSON schema.
    """
    duration_min = video_duration_sec / 60

    transcript_text = _format_transcript_blocks(transcript_segments)
    heatmap_text = _format_heatmap(heatmap)
    comments_text = _format_comments(comments)
    audio_text = _format_audio_spikes(audio_spikes)
    visual_text = _format_visual_spikes(visual_spikes)
    vault_text = _format_retention_vault(retention_vault_winners)
    lore_text = build_lore_context()

    prompt = f"""\
You are VICECLIP VIRAL BRAIN — the world's #1 AI YouTube Shorts clip selector \
specialised in GTA 6 content. Your job is to identify the 6-8 most viral-worthy \
short clips (15-58 seconds each) from the video below and return them as strict JSON.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VIDEO METADATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: {video_title}
Channel: {video_channel}
Duration: {duration_min:.1f} minutes ({video_duration_sec:.0f} seconds)
Type hint: {video_type_hint}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRANSCRIPT (timed blocks)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{transcript_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUTUBE "MOST REPLAYED" HEATMAP PEAKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{heatmap_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOP FAN COMMENTS WITH TIMESTAMPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{comments_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUDIO EXCITEMENT SPIKES (dB peaks — gunshots, explosions, screams)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{audio_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VISUAL VELOCITY SPIKES (silent high-action / physics moments)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{visual_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SELF-LEARNING RETENTION VAULT (Top-5 past winners)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{vault_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GTA 6 LORE & EASTER-EGG DICTIONARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{lore_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Analyse ALL the data above and select **6 to 8 clip candidates** ranked by \
overall viral potential. For each clip:

1. **Clip boundaries** (start_sec, end_sec): 15-58 seconds. Engineer the \
   clip for an **Infinite Loop** — the ending line/visual should flow \
   seamlessly into the opening hook so viewers re-watch involuntarily.

2. **4-Vector Virality Scorecard** (each 0-100):
   - `three_second_visual_hook`: How strong is the opening 3 seconds? \
     (Explosion? Shocking visual? Controversial text? Unexpected moment?)
   - `replay_loop_factor`: Does the ending loop into the beginning? \
     (10/10 = seamless infinite loop)
   - `debate_comment_bait_potential`: Will this spark comments / debate / saves? \
     (Hot takes? Controversial claim? "Am I the only one who noticed…?")
   - `payoff_speed`: How quickly does the clip deliver its payoff? \
     (Shorter = higher score. Avoid slow builds for Shorts.)

3. **Top Banner Texts** (A/B variants): Two different punchy 3-second \
   curiosity banners (max 40 chars each) that make viewers stop scrolling. \
   Use ALL CAPS where effective. Variant A and B should test different \
   angles (e.g., "ROCKSTAR DIDN'T WANT YOU TO SEE THIS" vs "LOOK WHAT I FOUND IN GTA 6").

4. **Easter Egg Detection**: If the clip contains a hidden detail, \
   background Easter egg, or subtle reference that most viewers would miss, \
   set `needs_easter_egg_zoom` to true and describe it.

5. **Upload Kit**: 3 viral title options (with emoji), targeted GTA 6 \
   hashtags, a debate-sparking pinned comment, and the best timestamp \
   for the Shorts cover thumbnail.

PRIORITISE:
- Moments where heatmap peaks + audio spikes + visual spikes converge
- Fan-comment-flagged moments (the community already validated these)
- GTA 6 lore-relevant reveals, Easter eggs, or callback moments
- Use Retention Vault winning patterns if available

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRICT OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Respond with ONLY valid JSON matching this exact schema (no markdown, \
no commentary, no explanation — just the JSON object):

{OUTPUT_JSON_SCHEMA}

CRITICAL: Return ONLY the JSON object. No markdown fences. No prose. \
Just the raw JSON starting with {{ and ending with }}.
"""
    return prompt


def build_commentary_script_prompt(
    *,
    clip_title: str,
    clip_transcript: str,
    clip_duration_sec: float,
    video_title: str,
) -> str:
    """
    Build a prompt for generating a transformative commentary script
    for the Transformative Commentary mode (Anti-"Reused Content").
    """
    target_words = int(clip_duration_sec * 2.8)

    return f"""\
You are a high-energy GTA 6 content commentator. Write a crisp, punchy \
commentary voiceover script for this YouTube Short clip.

CLIP CONTEXT:
- Video: {video_title}
- Clip title: {clip_title}
- Duration: {clip_duration_sec:.0f} seconds
- Original transcript: {clip_transcript[:500]}

REQUIREMENTS:
1. Script length: {target_words}-{target_words + 20} words (to fill {clip_duration_sec:.0f}s at natural pace)
2. Tone: Energetic, knowledgeable, hyped but not cringe
3. Add VALUE: explain what's happening, point out details viewers missed, \
   connect to GTA 6 lore, make comparisons
4. Opening hook: First sentence must be attention-grabbing (question, \
   shocking claim, or "look at this")
5. Ending: Close with a call-to-action or cliffhanger that makes viewers \
   want to replay or comment

Respond with ONLY the script text. No stage directions. No markdown. \
Just the spoken words, sentence by sentence, one per line.
"""
