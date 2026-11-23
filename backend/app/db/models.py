"""
VICECLIP STUDIO — Pydantic v2 Data Models
===========================================
Strongly-typed schemas for:
  • API request / response payloads
  • Gemini Viral Brain input → output validation
  • 4-Vector Virality Scorecard
  • Pipeline telemetry SSE events
  • System hardware status
"""

from __future__ import annotations

import json
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ═══════════════════════════════════════════════════════════════════════════════
# VIRALITY SCORECARD
# ═══════════════════════════════════════════════════════════════════════════════


class ViralityScorecard(BaseModel):
    """4-Vector virality scoring (each axis 0–100)."""

    three_second_visual_hook: float = Field(
        default=0, ge=0, le=100,
        description="Strength of the opening 3-second visual hook",
    )
    replay_loop_factor: float = Field(
        default=0, ge=0, le=100,
        description="How well the ending loops seamlessly into the opening",
    )
    debate_comment_bait_potential: float = Field(
        default=0, ge=0, le=100,
        description="Likelihood of sparking comments / debate / saves",
    )
    payoff_speed: float = Field(
        default=0, ge=0, le=100,
        description="How quickly the clip delivers its payoff",
    )

    @property
    def weighted_overall(self) -> float:
        """Weighted composite score (0–100)."""
        return round(
            self.three_second_visual_hook * 0.30
            + self.replay_loop_factor * 0.25
            + self.debate_comment_bait_potential * 0.25
            + self.payoff_speed * 0.20,
            1,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# UPLOAD KIT
# ═══════════════════════════════════════════════════════════════════════════════


class UploadKit(BaseModel):
    """YouTube Shorts upload metadata for one clip."""

    titles: list[str] = Field(
        default_factory=lambda: ["", "", ""],
        min_length=1,
        max_length=5,
        description="3 viral title options",
    )
    hashtags: list[str] = Field(default_factory=list)
    pinned_comment: str = Field(default="", description="Debate-sparking pinned comment")
    best_cover_timestamp_sec: float = Field(default=0, ge=0)


# ═══════════════════════════════════════════════════════════════════════════════
# CLIP CANDIDATE (Gemini output schema)
# ═══════════════════════════════════════════════════════════════════════════════


class ClipCandidate(BaseModel):
    """A single clip candidate from the Viral Brain."""

    clip_id: str = Field(description="Unique clip identifier")
    title_hook: str = Field(description="Punchy hook title for the clip")
    start_sec: float = Field(ge=0, description="Clip start in seconds")
    end_sec: float = Field(ge=0, description="Clip end in seconds")
    virality: ViralityScorecard = Field(default_factory=ViralityScorecard)
    top_banner_text_a: str = Field(default="", description="A/B variant A banner")
    top_banner_text_b: str = Field(default="", description="A/B variant B banner")
    needs_easter_egg_zoom: bool = Field(default=False)
    easter_egg_description: str = Field(default="")
    upload_kit: UploadKit = Field(default_factory=UploadKit)

    @property
    def duration_sec(self) -> float:
        return round(self.end_sec - self.start_sec, 1)

    @field_validator("end_sec")
    @classmethod
    def _end_after_start(cls, v: float, info: object) -> float:
        data = getattr(info, "data", {})
        start = data.get("start_sec", 0)
        if v <= start:
            raise ValueError(f"end_sec ({v}) must be > start_sec ({start})")
        return v


class ViralBrainResponse(BaseModel):
    """Complete validated response from the Gemini Viral Brain."""

    clips: list[ClipCandidate] = Field(min_length=1, max_length=10)
    analysis_summary: str = Field(default="")
    video_type: str = Field(
        default="gameplay",
        description="gameplay | trailer | breakdown | review",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PASS-1 SIGNAL MODELS
# ═══════════════════════════════════════════════════════════════════════════════


class TranscriptSegment(BaseModel):
    """Word-level transcription segment from faster-whisper."""

    text: str
    start: float
    end: float
    confidence: float = Field(default=0.0, ge=0, le=1)


class AudioSpike(BaseModel):
    """An audio excitement spike detected by librosa."""

    timestamp_sec: float
    db_level: float
    spike_type: str = Field(
        default="generic",
        description="gunshot | explosion | scream | music_hit | generic",
    )


class VisualSpike(BaseModel):
    """A visual action spike detected by opencv optical-flow sampling."""

    timestamp_sec: float
    velocity_score: float
    description: str = Field(default="")


class HeatmapPoint(BaseModel):
    """One segment of the YouTube 'Most Replayed' heatmap."""

    start_sec: float
    end_sec: float
    intensity: float = Field(ge=0, le=1)


class TimestampedComment(BaseModel):
    """A YouTube comment with an extracted ``MM:SS`` timestamp."""

    text: str
    timestamp_sec: float
    likes: int = Field(default=0)


# ═══════════════════════════════════════════════════════════════════════════════
# API REQUEST / RESPONSE PAYLOADS
# ═══════════════════════════════════════════════════════════════════════════════


class RenderSettings(BaseModel):
    """User-configurable per-job render settings."""

    enable_demucs: bool = Field(default=False, description="Strip copyrighted music")
    enable_commentary: bool = Field(default=False, description="Transformative commentary via edge-tts")
    enable_easter_egg_zoom: bool = Field(default=True, description="Auto-zoom Easter eggs")
    enable_dead_air_cut: bool = Field(default=True, description="Cut silence > 0.4s")
    enable_dual_hook: bool = Field(default=True, description="A/B hook variant export")
    caption_theme: str = Field(
        default="vice_city_neon",
        description="vice_city_neon | rockstar_bold | clean_minimal",
    )
    manual_gemini_mode: bool = Field(default=False, description="Manual copy-paste Gemini web mode")
    commentary_voice: str = Field(default="en-US-GuyNeural", description="edge-tts voice name")
    custom_crop: Optional[dict] = Field(default=None, description="Custom 9:16 crop box {x, y, w, h}")


class AnalyzeRequest(BaseModel):
    """Request body to start analysing a YouTube video."""

    url: str = Field(description="YouTube video URL")
    settings: Optional[RenderSettings] = None


class BatchQueueRequest(BaseModel):
    """Request body to add multiple URLs to the batch watchlist."""

    urls: list[str] = Field(min_length=1, max_length=10)
    settings: Optional[RenderSettings] = None


class ManualGeminiInput(BaseModel):
    """
    User-pasted JSON response from the Gemini Web app.
    The ``parse_clips`` method validates against ViralBrainResponse.
    """

    json_text: str = Field(description="Raw JSON pasted from gemini.google.com")

    def parse_clips(self) -> ViralBrainResponse:
        raw = json.loads(self.json_text)
        return ViralBrainResponse.model_validate(raw)


class TrimAdjustment(BaseModel):
    """Frontend 0.1s precision trim nudge for a clip."""

    clip_id: str
    start_sec: float = Field(ge=0)
    end_sec: float = Field(ge=0)


class CropOverride(BaseModel):
    """Frontend custom 9:16 crop box override."""

    clip_id: str
    x: float = Field(ge=0, le=1, description="Normalised x offset")
    y: float = Field(ge=0, le=1, description="Normalised y offset")
    w: float = Field(gt=0, le=1, description="Normalised width")
    h: float = Field(gt=0, le=1, description="Normalised height")


# ═══════════════════════════════════════════════════════════════════════════════
# RETENTION VAULT PAYLOADS
# ═══════════════════════════════════════════════════════════════════════════════


class RetentionVaultEntry(BaseModel):
    """Full retention vault row for creation."""

    clip_id: str
    video_id: str
    title_hook: str = ""
    views_48h: int = Field(default=0, ge=0)
    avd_pct: float = Field(default=0, ge=0, le=100)
    viewed_pct: float = Field(default=0, ge=0, le=100)
    swiped_pct: float = Field(default=0, ge=0, le=100)
    hook_formula: str = ""
    clip_pattern: str = ""
    banner_text: str = ""
    notes: str = ""


class RetentionVaultUpdate(BaseModel):
    """Partial update for a retention vault entry."""

    views_48h: Optional[int] = None
    avd_pct: Optional[float] = None
    viewed_pct: Optional[float] = None
    swiped_pct: Optional[float] = None
    hook_formula: Optional[str] = None
    clip_pattern: Optional[str] = None
    notes: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# TELEMETRY & STATUS
# ═══════════════════════════════════════════════════════════════════════════════


class PipelineTelemetry(BaseModel):
    """Real-time pipeline status pushed via SSE."""

    job_id: int = 0
    video_id: str = ""
    stage: str = "idle"
    stage_label: str = "Idle"
    progress_pct: float = 0
    eta_seconds: float = 0
    vram_used_mb: int = 0
    vram_total_mb: int = 6144
    vram_pct: float = 0
    log_message: str = ""
    is_complete: bool = False
    error: Optional[str] = None


class SystemStatus(BaseModel):
    """Hardware + capability snapshot returned by /api/status."""

    ffmpeg_available: bool = False
    nvenc_available: bool = False
    cuda_available: bool = False
    cuda_device: Optional[str] = None
    vram_total_mb: int = 6144
    encoder: str = "libx264"
    python_version: str = ""
    workspace_dir: str = ""


class GeminiTestResult(BaseModel):
    """Result of the 'Test Gemini Connection' endpoint."""

    success: bool
    model_name: str = ""
    available_models: list[str] = Field(default_factory=list)
    error: Optional[str] = None
    response_preview: str = ""


class SettingsResponse(BaseModel):
    """Safe-to-expose subset of current application settings."""

    gemini_api_key_set: bool = False
    gemini_fast_model: str = ""
    gemini_deep_model: str = ""
    whisper_model_size: str = "small"
    nvenc_preset: str = "p4"
    target_fps: int = 60
    caption_theme: str = "vice_city_neon"
    output_dir: str = ""
