"""
VICECLIP STUDIO — Signal Analyzer  (Pass 1)
=============================================
Fast multi-modal excitement spike detection:
  1. Audio dB spikes (librosa): gunshots, explosions, screams, music hits.
  2. Visual velocity spikes (OpenCV / FFmpeg): fast action, vehicle chases, physics ragdolls.
     Optimized to sample 1 fps downscaled frames in < 3 seconds.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import cv2
import librosa
import numpy as np

from app.db.models import AudioSpike, VisualSpike

logger = logging.getLogger("viceclip.signals")

_WIN_CREATE_NO_WINDOW: int = 0x08000000 if os.name == "nt" else 0


def _get_ffmpeg_cmd() -> str:
    """Finds working FFmpeg binary path."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    winget_path = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"
    if winget_path.is_dir():
        for p in winget_path.glob("**/ffmpeg.exe"):
            return str(p)
    return "ffmpeg"


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIO SPIKE DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def _analyse_audio_sync(
    audio_path: str,
    sr: int = 22050,
    hop_length: int = 512,
    top_n: int = 30,
) -> list[AudioSpike]:
    """
    Computes RMS excitement spikes and classifies by spectral centroid.
    Returns typed AudioSpike models.
    """
    src = str(Path(audio_path).resolve())
    logger.info("Loading audio for spike detection: %s", Path(src).name)

    try:
        y, actual_sr = librosa.load(src, sr=sr, mono=True)
    except Exception:
        # Fallback to ffmpeg extraction if format needs decoders
        tmp_wav = str(Path(src).with_suffix(".tmp.wav"))
        ff = _get_ffmpeg_cmd()
        cmd = [ff, "-y", "-loglevel", "error", "-i", src, "-ar", str(sr), "-ac", "1", tmp_wav]
        subprocess.run(cmd, check=True, creationflags=_WIN_CREATE_NO_WINDOW)
        try:
            y, actual_sr = librosa.load(tmp_wav, sr=sr, mono=True)
        finally:
            if os.path.isfile(tmp_wav):
                try:
                    os.remove(tmp_wav)
                except OSError:
                    pass

    if y.size == 0:
        return []

    # RMS in dB
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)

    # Rolling median baseline
    win = max(5, int(3.0 * actual_sr / hop_length))
    if win % 2 == 0:
        win += 1

    baseline = np.zeros_like(rms_db)
    half = win // 2
    for i in range(len(rms_db)):
        lo = max(0, i - half)
        hi = min(len(rms_db), i + half + 1)
        baseline[i] = float(np.median(rms_db[lo:hi]))

    # Excitement threshold: baseline + 6 dB
    spike_indices = np.where(rms_db > baseline + 6.0)[0]
    if len(spike_indices) == 0:
        return []

    # Spectral centroids for classification
    centroids = librosa.feature.spectral_centroid(y=y, sr=actual_sr, hop_length=hop_length)[0]

    spikes: list[AudioSpike] = []
    last_t = -10.0

    for idx in spike_indices:
        t = float(librosa.frames_to_time(idx, sr=actual_sr, hop_length=hop_length))
        if t - last_t < 1.5:  # merge nearby peaks
            continue
        last_t = t

        c_val = float(centroids[min(idx, len(centroids) - 1)])
        if c_val < 1500:
            stype = "explosion"
        elif c_val > 5000:
            stype = "scream"
        elif 2000 < c_val < 4000:
            stype = "gunshot"
        else:
            stype = "generic"

        spikes.append(
            AudioSpike(
                timestamp_sec=round(t, 2),
                db_level=round(float(rms_db[idx]), 1),
                spike_type=stype,
            )
        )

    # Sort by dB descending and take top N
    spikes.sort(key=lambda s: s.db_level, reverse=True)
    res = spikes[:top_n]
    res.sort(key=lambda s: s.timestamp_sec)
    logger.info("Detected %d audio excitement spikes", len(res))
    return res


# ═══════════════════════════════════════════════════════════════════════════════
# FAST VISUAL SPIKE DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def _analyse_visual_sync(
    video_path: str,
    sample_fps: float = 1.0,
    top_n: int = 20,
) -> list[VisualSpike]:
    """
    Fast visual velocity detection.
    Extracts 1 fps downscaled 160x90 frames via FFmpeg or fast OpenCV
    in < 3 seconds total.
    """
    src = str(Path(video_path).resolve())
    ff = _get_ffmpeg_cmd()

    diffs: list[tuple[float, float]] = []

    # Method A: Fast FFmpeg Rawvideo Pipe (1-2 seconds for whole video)
    try:
        cmd = [
            ff, "-y", "-loglevel", "error",
            "-i", src,
            "-vf", f"fps={sample_fps:.1f},scale=160:90",
            "-f", "rawvideo", "-pix_fmt", "gray", "-",
        ]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=_WIN_CREATE_NO_WINDOW,
        )
        raw_bytes, _ = proc.communicate(timeout=25)

        w, h = 160, 90
        frame_size = w * h
        total_frames = len(raw_bytes) // frame_size

        prev_frame: Optional[np.ndarray] = None
        for i in range(total_frames):
            frame_data = raw_bytes[i * frame_size : (i + 1) * frame_size]
            arr = np.frombuffer(frame_data, dtype=np.uint8).astype(np.float32)
            ts = i / sample_fps

            if prev_frame is not None:
                velocity = float(np.mean(np.abs(arr - prev_frame)))
                diffs.append((ts, velocity))
            prev_frame = arr

    except Exception as exc:
        logger.warning("FFmpeg fast visual sampling failed: %s. Using OpenCV fallback.", exc)
        diffs.clear()

        # Method B: OpenCV Fallback with large step
        cap = cv2.VideoCapture(src)
        if cap.isOpened():
            native_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            step = max(1, int(round(native_fps / sample_fps)))

            prev = None
            f_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret or f_idx > total_f:
                    break
                if f_idx % step == 0:
                    small = cv2.resize(frame, (160, 90), interpolation=cv2.INTER_AREA)
                    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32)
                    if prev is not None:
                        diffs.append((f_idx / native_fps, float(np.mean(np.abs(gray - prev)))))
                    prev = gray
                f_idx += 1
            cap.release()

    if not diffs:
        return []

    vals = np.array([d[1] for d in diffs], dtype=np.float32)
    mean_v = float(np.mean(vals))
    std_v = float(np.std(vals))
    threshold = mean_v + (1.2 * std_v)

    raw_spikes = [(ts, score) for ts, score in diffs if score > threshold]
    if not raw_spikes and len(diffs) > 0:
        p80 = float(np.percentile(vals, 80))
        raw_spikes = [(ts, score) for ts, score in diffs if score >= p80]

    # Merge nearby peaks
    merged: list[tuple[float, float]] = []
    if raw_spikes:
        best_t, best_s = raw_spikes[0]
        for ts, score in raw_spikes[1:]:
            if ts - best_t < 2.0:
                if score > best_s:
                    best_t, best_s = ts, score
            else:
                merged.append((best_t, best_s))
                best_t, best_s = ts, score
        merged.append((best_t, best_s))

    spikes: list[VisualSpike] = []
    for ts, score in merged:
        ratio = score / mean_v if mean_v > 0 else 1.0
        desc = "extreme_action" if ratio > 2.2 else "high_action" if ratio > 1.6 else "moderate_action"
        spikes.append(
            VisualSpike(
                timestamp_sec=round(ts, 2),
                velocity_score=round(score, 2),
                description=desc,
            )
        )

    spikes.sort(key=lambda s: s.velocity_score, reverse=True)
    res = spikes[:top_n]
    res.sort(key=lambda s: s.timestamp_sec)
    logger.info("Detected %d visual action spikes", len(res))
    return res


# ═══════════════════════════════════════════════════════════════════════════════
# ASYNC WRAPPER
# ═══════════════════════════════════════════════════════════════════════════════

async def detect_audio_spikes(audio_path: str, sr: int = 22050) -> list[AudioSpike]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _analyse_audio_sync, audio_path, sr)


async def detect_visual_spikes(video_path: str, sample_fps: float = 1.0) -> list[VisualSpike]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _analyse_visual_sync, video_path, sample_fps)


async def analyse_signals(video_path: str, audio_path: str) -> tuple[list[AudioSpike], list[VisualSpike]]:
    """Runs audio dB and visual velocity detection in parallel."""
    return await asyncio.gather(
        detect_audio_spikes(audio_path),
        detect_visual_spikes(video_path),
    )
