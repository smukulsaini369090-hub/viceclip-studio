"""
VICECLIP STUDIO — Transformative Commentary Engine  (Pass 4 Stage D)
=====================================================================
Transforms raw gameplay clips into monetisation-safe YouTube Shorts:
  1. Synthesises energetic AI voiceover scripts via `edge-tts`.
  2. WINDOWS 11 HARDENING: Executes `edge-tts` via dedicated isolated subprocess calls
     (`python -m edge_tts`) to completely bypass Windows ProactorEventLoop
     `RuntimeError: Event loop is closed` or conflict bugs with FastAPI.
  3. Automatically ducks background gameplay audio to -18 dB and mixes commentary voiceover.
  4. Generates timed word boundaries so dynamic captions sync directly to commentary.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.config import get_settings
from app.core.gemini_brain import run_commentary_api
from app.db.models import TranscriptSegment

logger = logging.getLogger("viceclip.commentary")

_WIN_CREATE_NO_WINDOW: int = 0x08000000 if sys.platform == "win32" else 0

AVAILABLE_VOICES: dict[str, str] = {
    "en-US-GuyNeural": "Energetic Male (Default)",
    "en-US-ChristopherNeural": "Hype Broadcaster Male",
    "en-US-JennyNeural": "Energetic Female",
    "en-US-AriaNeural": "Fast-Paced News Female",
    "en-GB-RyanNeural": "British Gaming Commentary Male",
}


@dataclass
class CommentaryResult:
    """Result of commentary generation and synthesis."""
    script_text: str
    voice_audio_path: str
    mixed_audio_path: str
    duration_sec: float
    segments: list[TranscriptSegment]


def _run_cmd(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    """Run subprocess silently on Windows."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=_WIN_CREATE_NO_WINDOW,
    )


def synthesize_speech_isolated_sync(
    text: str,
    output_audio_path: str,
    voice: str = "en-US-GuyNeural",
    rate: str = "+10%",
    pitch: str = "+0Hz",
) -> str:
    """
    Synthesizes speech using `edge-tts` inside an isolated Python subprocess.
    This guarantees 100% safety against Windows Proactor loop closure crashes.
    """
    out_file = Path(output_audio_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Clean text to prevent CLI injection
    clean_text = text.replace('"', '\\"').replace("\n", " ").strip()

    # Small runner script invoked via python -c
    script = (
        "import asyncio, edge_tts, sys\n"
        "async def main():\n"
        f"    tts = edge_tts.Communicate(r'''{clean_text}''', voice='{voice}', rate='{rate}', pitch='{pitch}')\n"
        f"    await tts.save(r'''{str(out_file)}''')\n"
        "asyncio.run(main())\n"
    )

    cmd = [sys.executable, "-c", script]
    res = _run_cmd(cmd, timeout=90)

    if res.returncode != 0 or not out_file.is_file() or out_file.stat().st_size == 0:
        logger.error("edge-tts subprocess failed (code %d): %s", res.returncode, res.stderr)
        raise RuntimeError(f"edge-tts synthesis failed: {res.stderr}")

    logger.info("Synthesized commentary voiceover: %s (%.1f KB)", out_file.name, out_file.stat().st_size / 1024)
    return str(out_file)


def mix_commentary_with_gameplay_sync(
    commentary_audio_path: str,
    gameplay_audio_path: str,
    output_audio_path: str,
    gameplay_duck_db: float = -18.0,
) -> str:
    """
    Composites commentary voiceover with gameplay audio ducked to -18 dB.
    Uses FFmpeg `volume` filter + `amix`.
    """
    settings = get_settings()
    ffmpeg_bin = settings.ffmpeg_path

    out_file = Path(output_audio_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Gameplay volume lowered to specified ducking dB (e.g. -18dB ~= 0.125 volume)
    # Commentary voice kept clean at 1.0 (0 dB)
    duck_factor = 10.0 ** (gameplay_duck_db / 20.0)

    cmd = [
        ffmpeg_bin, "-y", "-loglevel", "error",
        "-i", str(Path(commentary_audio_path).resolve()),
        "-i", str(Path(gameplay_audio_path).resolve()),
        "-filter_complex",
        f"[0:a]volume=1.1[voice];[1:a]volume={duck_factor:.3f}[gameplay];[voice][gameplay]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-c:a", "aac", "-b:a", "192k",
        str(out_file),
    ]

    res = _run_cmd(cmd, timeout=60)
    if res.returncode != 0:
        logger.warning("FFmpeg ducking mix failed (%d): %s. Falling back to voice only.", res.returncode, res.stderr)
        cmd_fb = [
            ffmpeg_bin, "-y", "-loglevel", "error",
            "-i", str(Path(commentary_audio_path).resolve()),
            "-c:a", "aac", "-b:a", "192k",
            str(out_file),
        ]
        _run_cmd(cmd_fb)

    return str(out_file)


async def generate_transformative_commentary(
    clip_title: str,
    clip_transcript: str,
    clip_duration_sec: float,
    video_title: str,
    gameplay_audio_path: str,
    output_dir: str,
    clip_id: str,
    voice: str = "en-US-GuyNeural",
    script_override: Optional[str] = None,
) -> CommentaryResult:
    """
    Orchestrates transformative commentary:
      1. Generates voiceover script via Gemini (or uses manual script override).
      2. Synthesizes voiceover safely using isolated edge-tts worker.
      3. Mixes audio ducking original gameplay to -18 dB.
      4. Transcribes the new commentary to produce word-level timestamps.
    """
    settings = get_settings()
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Script Generation
    if script_override and script_override.strip():
        script_text = script_override.strip()
    else:
        try:
            script_text = await run_commentary_api(
                clip_title=clip_title,
                clip_transcript=clip_transcript,
                clip_duration_sec=clip_duration_sec,
                video_title=video_title,
            )
        except Exception as exc:
            logger.warning("Gemini commentary generation failed: %s. Using emergency script template.", exc)
            script_text = (
                f"Check out this insane GTA 6 moment! Notice how the RAGE 9 engine handles "
                f"the physics and lighting right here. Most people completely missed this detail, "
                f"so pay close attention to what happens next!"
            )

    voice_audio = str(out_dir / f"{clip_id}_commentary_voice.wav")
    mixed_audio = str(out_dir / f"{clip_id}_commentary_mixed.m4a")

    loop = asyncio.get_running_loop()

    # 2. Isolated speech synthesis
    await loop.run_in_executor(
        None,
        synthesize_speech_isolated_sync,
        script_text,
        voice_audio,
        voice,
        "+10%",
        "+0Hz",
    )

    # 3. Audio ducking mix
    await loop.run_in_executor(
        None,
        mix_commentary_with_gameplay_sync,
        voice_audio,
        gameplay_audio_path,
        mixed_audio,
        -18.0,
    )

    # 4. Transcribe commentary voiceover with Whisper for exact subtitle sync
    from app.core.transcriber import transcribe_audio
    commentary_segments = await transcribe_audio(voice_audio)

    # Get actual synthesized duration
    duration_sec = clip_duration_sec
    if commentary_segments:
        duration_sec = max(clip_duration_sec, commentary_segments[-1].end)

    return CommentaryResult(
        script_text=script_text,
        voice_audio_path=voice_audio,
        mixed_audio_path=mixed_audio,
        duration_sec=duration_sec,
        segments=commentary_segments,
    )
