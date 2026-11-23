"""
VICECLIP STUDIO — YouTube Extractor  (Pass 1)
================================================
Downloads video + audio, extracts YouTube "Most Replayed" heatmap and
top-50 comments via ``yt-dlp``.  Gracefully handles videos where heatmap
or comments are missing / disabled without crashing.

Comment timestamps (``MM:SS`` or ``H:MM:SS``) are regex-parsed into
exact seconds so the Viral Brain can correlate fan-flagged moments.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Optional

from app.config import get_settings
from app.db.models import HeatmapPoint, TimestampedComment

logger = logging.getLogger("viceclip.extractor")

# ═══════════════════════════════════════════════════════════════════════════════
# VIDEO-ID NORMALISATION
# ═══════════════════════════════════════════════════════════════════════════════

_YT_ID_RE = re.compile(
    r"""(?:youtube\.com/(?:watch\?.*?v=|embed/|v/|shorts/|live/)
        |youtu\.be/)
        (?P<id>[A-Za-z0-9_-]{11})""",
    re.VERBOSE,
)
_BARE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def normalize_video_id(url_or_id: str) -> str:
    """
    Extract the 11-character YouTube video ID from any URL variant,
    or return the string as-is if it already looks like a bare ID.

    Raises ``ValueError`` if no valid ID can be found.
    """
    url_or_id = url_or_id.strip()
    if _BARE_ID_RE.match(url_or_id):
        return url_or_id
    m = _YT_ID_RE.search(url_or_id)
    if m:
        return m.group("id")
    raise ValueError(f"Cannot extract YouTube video ID from: {url_or_id!r}")


# ═══════════════════════════════════════════════════════════════════════════════
# TIMESTAMP PARSING FROM COMMENT TEXT
# ═══════════════════════════════════════════════════════════════════════════════

_TS_RE = re.compile(r"\b(?:(\d{1,2}):)?(\d{1,2}):(\d{2})\b")


def parse_comment_timestamps(text: str) -> list[float]:
    """
    Find every ``MM:SS`` or ``H:MM:SS`` timestamp in *text* and return
    them as a list of seconds.
    """
    results: list[float] = []
    for m in _TS_RE.finditer(text):
        hours = int(m.group(1)) if m.group(1) else 0
        minutes = int(m.group(2))
        seconds = int(m.group(3))
        total = hours * 3600 + minutes * 60 + seconds
        results.append(float(total))
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# HEATMAP EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════


def _extract_heatmap(info: dict) -> list[HeatmapPoint]:
    """
    Pull the Most Replayed heatmap from yt-dlp's ``info_dict``.
    Returns an empty list (never crashes) if the video has no heatmap.
    """
    raw = info.get("heatmap")
    if not raw:
        logger.info("No Most Replayed heatmap available for this video")
        return []

    points: list[HeatmapPoint] = []
    for entry in raw:
        try:
            points.append(
                HeatmapPoint(
                    start_sec=float(entry.get("start_time", entry.get("start", 0))),
                    end_sec=float(entry.get("end_time", entry.get("end", 0))),
                    intensity=float(entry.get("value", entry.get("intensity", 0))),
                )
            )
        except (TypeError, ValueError) as exc:
            logger.debug("Skipping malformed heatmap entry %s: %s", entry, exc)
    logger.info("Extracted %d heatmap segments", len(points))
    return points


# ═══════════════════════════════════════════════════════════════════════════════
# COMMENT EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════


def _extract_comments(info: dict, max_comments: int = 50) -> list[TimestampedComment]:
    """
    Pull top comments from yt-dlp's ``info_dict``, regex-parse any
    ``MM:SS`` / ``H:MM:SS`` timestamps, and return only comments that
    contain at least one timestamp.

    Returns an empty list if comments are disabled / unavailable.
    """
    raw_comments = info.get("comments")
    if not raw_comments:
        logger.info("No comments available for this video")
        return []

    timestamped: list[TimestampedComment] = []
    for c in raw_comments[:max_comments * 3]:
        text = c.get("text", "")
        if not text:
            continue
        timestamps = parse_comment_timestamps(text)
        if not timestamps:
            continue
        likes = int(c.get("like_count", 0) or 0)
        for ts in timestamps:
            timestamped.append(
                TimestampedComment(text=text, timestamp_sec=ts, likes=likes)
            )

    timestamped.sort(key=lambda x: x.likes, reverse=True)
    result = timestamped[:max_comments]
    logger.info(
        "Extracted %d timestamped comments (from %d total)",
        len(result),
        len(raw_comments),
    )
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════


class ExtractionResult:
    """Container for all data returned by ``extract_video``."""

    __slots__ = (
        "video_id",
        "url",
        "title",
        "channel",
        "duration_sec",
        "thumbnail_url",
        "video_path",
        "audio_path",
        "heatmap",
        "comments",
        "info_dict",
    )

    def __init__(
        self,
        video_id: str,
        url: str,
        title: str,
        channel: str,
        duration_sec: float,
        thumbnail_url: str,
        video_path: str,
        audio_path: str,
        heatmap: list[HeatmapPoint],
        comments: list[TimestampedComment],
        info_dict: dict,
    ) -> None:
        self.video_id = video_id
        self.url = url
        self.title = title
        self.channel = channel
        self.duration_sec = duration_sec
        self.thumbnail_url = thumbnail_url
        self.video_path = video_path
        self.audio_path = audio_path
        self.heatmap = heatmap
        self.comments = comments
        self.info_dict = info_dict

    def to_cache_dict(self) -> dict:
        """Serialise to a dict suitable for ``cache_upsert_video``."""
        return {
            "video_id": self.video_id,
            "url": self.url,
            "title": self.title,
            "channel": self.channel,
            "duration_sec": self.duration_sec,
            "thumbnail_url": self.thumbnail_url,
            "transcript_json": "[]",
            "heatmap_json": [hp.model_dump() for hp in self.heatmap],
            "comments_json": [tc.model_dump() for tc in self.comments],
            "audio_spikes_json": "[]",
            "visual_spikes_json": "[]",
            "download_path": self.video_path,
            "audio_path": self.audio_path,
        }


async def extract_video(
    url: str,
    *,
    max_comments: int = 50,
    max_resolution: int = 1080,
) -> ExtractionResult:
    """
    Download a YouTube video + audio and extract metadata via yt-dlp.

    Parameters
    ----------
    url : str
        Any YouTube URL or bare 11-character video ID.
    max_comments : int
        Maximum timestamped comments to return.
    max_resolution : int
        Max vertical resolution for the video download (default 1080p).

    Returns
    -------
    ExtractionResult
        All extracted data bundled together.
    """
    import asyncio
    import yt_dlp

    settings = get_settings()
    video_id = normalize_video_id(url)
    canonical_url = f"https://www.youtube.com/watch?v={video_id}"

    cache_dir = Path(settings.cache_dir) / video_id
    cache_dir.mkdir(parents=True, exist_ok=True)

    video_path = str(cache_dir / f"{video_id}.mp4")
    audio_path = str(cache_dir / f"{video_id}.m4a")

    logger.info("Extracting video: %s  (ID: %s)", canonical_url, video_id)

    # ── Phase 1: Download video + audio ──────────────────────────────────────

    video_opts: dict = {
        "format": f"bestvideo[height<={max_resolution}][ext=mp4]+bestaudio[ext=m4a]/best[height<={max_resolution}][ext=mp4]/best",
        "merge_output_format": "mp4",
        "outtmpl": str(cache_dir / f"{video_id}.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "overwrites": False,
        "retries": 3,
        "fragment_retries": 3,
        "socket_timeout": 30,
        "getcomments": True,
        "extractor_args": {
            "youtube": {
                "comment_sort": ["top"],
                "max_comments": [str(max_comments * 3), "0", "0", "0"],
            }
        },
        "postprocessors": [],
    }

    info: dict = {}

    def _run_download() -> dict:
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            return ydl.extract_info(canonical_url, download=True)

    loop = asyncio.get_running_loop()
    info = await loop.run_in_executor(None, _run_download)

    # ── Locate downloaded files ──────────────────────────────────────────────

    actual_video = video_path
    if not os.path.isfile(actual_video):
        for f in cache_dir.iterdir():
            if f.suffix == ".mp4" and f.stem.startswith(video_id):
                actual_video = str(f)
                break

    # ── Phase 2: Extract separate audio if not already present ───────────────

    if not os.path.isfile(audio_path):
        audio_opts: dict = {
            "format": "bestaudio[ext=m4a]/bestaudio",
            "outtmpl": str(cache_dir / f"{video_id}.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "overwrites": False,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                    "preferredquality": "192",
                }
            ],
        }

        def _run_audio() -> None:
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([canonical_url])

        try:
            await loop.run_in_executor(None, _run_audio)
        except Exception as exc:
            logger.warning("Separate audio download failed: %s — will extract from video", exc)

    # Find actual audio file
    actual_audio = audio_path
    if not os.path.isfile(actual_audio):
        for ext in (".m4a", ".webm", ".opus", ".mp3"):
            candidate = cache_dir / f"{video_id}{ext}"
            if candidate.is_file():
                actual_audio = str(candidate)
                break

    # If still no separate audio, we'll use the video file itself
    if not os.path.isfile(actual_audio):
        actual_audio = actual_video
        logger.info("Using video file as audio source: %s", actual_audio)

    # ── Phase 3: Extract heatmap & comments ──────────────────────────────────

    heatmap = _extract_heatmap(info)
    comments = _extract_comments(info, max_comments=max_comments)

    # ── Build result ─────────────────────────────────────────────────────────

    title = info.get("title", info.get("fulltitle", ""))
    channel = info.get("uploader", info.get("channel", ""))
    duration = float(info.get("duration", 0) or 0)
    thumb = info.get("thumbnail", "")

    result = ExtractionResult(
        video_id=video_id,
        url=canonical_url,
        title=title,
        channel=channel,
        duration_sec=duration,
        thumbnail_url=thumb,
        video_path=actual_video,
        audio_path=actual_audio,
        heatmap=heatmap,
        comments=comments,
        info_dict=info,
    )

    logger.info(
        "Extraction complete: '%s' by %s (%.0fs) — %d heatmap pts, %d comments",
        title,
        channel,
        duration,
        len(heatmap),
        len(comments),
    )
    return result
