"""
VICECLIP STUDIO — Transcriber  (Pass 1)
=========================================
Word-level transcription via ``faster-whisper`` on CUDA (``int8_float16``).

* Runs **strictly inside** ``VRAMManager.acquire_gpu(GPUStage.WHISPER)``
  so only one GPU stage is active at a time.
* Immediately unloads the model on exit (``del model``, ``gc.collect()``,
  ``torch.cuda.empty_cache()``) to free VRAM for subsequent stages.
* Falls back to CPU transparently if CUDA is unavailable.
"""

from __future__ import annotations

import gc
import logging
from pathlib import Path
from typing import Optional

from app.config import get_settings
from app.core.vram_manager import GPUStage, get_vram_manager, flush_gpu_memory
from app.db.models import TranscriptSegment

logger = logging.getLogger("viceclip.transcriber")


async def transcribe_audio(
    audio_path: str | Path,
    *,
    model_size: Optional[str] = None,
    compute_type: Optional[str] = None,
    language: Optional[str] = None,
) -> list[TranscriptSegment]:
    """
    Transcribe an audio file and return word-level segments.

    Parameters
    ----------
    audio_path : str | Path
        Path to the audio file (m4a, wav, mp3, etc.).
    model_size : str, optional
        Whisper model size (``tiny``, ``base``, ``small``, ``medium``).
        Defaults to ``settings.whisper_model_size``.
    compute_type : str, optional
        Quantisation type. Defaults to ``settings.whisper_compute_type``.
    language : str, optional
        ISO 639-1 language code (``en``). ``None`` = auto-detect.

    Returns
    -------
    list[TranscriptSegment]
        Flattened word-level segments with timestamps and confidence.
    """
    import asyncio

    settings = get_settings()
    mgr = get_vram_manager()

    model_size = model_size or settings.whisper_model_size
    compute_type = compute_type or settings.whisper_compute_type
    device = settings.whisper_device

    audio_path = str(Path(audio_path).resolve())
    if not Path(audio_path).is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    logger.info(
        "Transcribing: %s  (model=%s, device=%s, compute=%s)",
        audio_path, model_size, device, compute_type,
    )

    segments_out: list[TranscriptSegment] = []

    async with mgr.acquire_gpu(GPUStage.WHISPER):
        loop = asyncio.get_running_loop()
        segments_out = await loop.run_in_executor(
            None,
            _run_whisper_sync,
            audio_path,
            model_size,
            compute_type,
            device,
            language,
        )

    logger.info("Transcription complete: %d word segments", len(segments_out))
    return segments_out


def _run_whisper_sync(
    audio_path: str,
    model_size: str,
    compute_type: str,
    device: str,
    language: Optional[str],
) -> list[TranscriptSegment]:
    """
    Synchronous whisper transcription — runs inside a thread executor
    while the VRAMManager GPU lock is held.

    The model is loaded, used, and **immediately destroyed** to free VRAM.
    """
    from faster_whisper import WhisperModel

    model: Optional[WhisperModel] = None

    try:
        # ── Determine device ─────────────────────────────────────────────────
        actual_device = device
        actual_compute = compute_type

        if actual_device == "cuda":
            try:
                import torch
                if not torch.cuda.is_available():
                    logger.warning("CUDA requested but unavailable — falling back to CPU")
                    actual_device = "cpu"
                    actual_compute = "int8"
            except ImportError:
                logger.warning("PyTorch not installed — falling back to CPU")
                actual_device = "cpu"
                actual_compute = "int8"

        # ── Load model ───────────────────────────────────────────────────────
        logger.info(
            "Loading faster-whisper model: %s (device=%s, compute=%s)",
            model_size, actual_device, actual_compute,
        )
        model = WhisperModel(
            model_size,
            device=actual_device,
            compute_type=actual_compute,
        )

        # ── Transcribe with word-level timestamps ────────────────────────────
        raw_segments, info = model.transcribe(
            audio_path,
            word_timestamps=True,
            language=language,
            vad_filter=False,
            vad_parameters=dict(
                min_silence_duration_ms=300,
                speech_pad_ms=200,
            ),
        )

        logger.info(
            "Whisper detected language: %s (probability=%.2f)",
            info.language,
            info.language_probability,
        )

        # ── Flatten to word-level segments ───────────────────────────────────
        segments_out: list[TranscriptSegment] = []

        for segment in raw_segments:
            if segment.words:
                for word in segment.words:
                    segments_out.append(
                        TranscriptSegment(
                            text=word.word.strip(),
                            start=round(word.start, 3),
                            end=round(word.end, 3),
                            confidence=round(word.probability, 4),
                        )
                    )
            else:
                segments_out.append(
                    TranscriptSegment(
                        text=segment.text.strip(),
                        start=round(segment.start, 3),
                        end=round(segment.end, 3),
                        confidence=round(segment.avg_logprob, 4) if segment.avg_logprob else 0.0,
                    )
                )

        return segments_out

    finally:
        # ── CRITICAL: unload model immediately ──────────────────────────────
        if model is not None:
            logger.info("Unloading Whisper model from VRAM ...")
            del model
        flush_gpu_memory()
        logger.info("Whisper model unloaded — VRAM freed")


def segments_to_text(segments: list[TranscriptSegment]) -> str:
    """Join word segments into a single readable transcript string."""
    return " ".join(seg.text for seg in segments)


def segments_to_timed_blocks(
    segments: list[TranscriptSegment],
    block_duration_sec: float = 10.0,
) -> list[dict]:
    """
    Group word segments into timed blocks for structured prompt input.

    Returns a list of ``{start, end, text}`` dicts, each covering
    roughly *block_duration_sec* of audio.
    """
    if not segments:
        return []

    blocks: list[dict] = []
    block_start = segments[0].start
    block_words: list[str] = []

    for seg in segments:
        block_words.append(seg.text)
        if seg.end - block_start >= block_duration_sec:
            blocks.append({
                "start": round(block_start, 2),
                "end": round(seg.end, 2),
                "text": " ".join(block_words),
            })
            block_start = seg.end
            block_words = []

    if block_words:
        blocks.append({
            "start": round(block_start, 2),
            "end": round(segments[-1].end, 2),
            "text": " ".join(block_words),
        })

    return blocks
