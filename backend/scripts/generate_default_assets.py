"""
VICECLIP STUDIO — Default Asset Generator
===========================================
Synthesises clean starter SFX and a copyright-free synthwave pulse loop
so the renderer NEVER crashes if the user hasn't added custom audio files.

Generated assets
  assets/sfx/whoosh.wav       — cinematic transition whoosh  (0.5 s)
  assets/sfx/riser.wav        — tension-building riser       (1.5 s)
  assets/sfx/bass_hit.wav     — punchy 808-style bass hit    (0.4 s)
  assets/music/default_synthwave_loop.wav — 16 s @ 110 BPM retrowave loop

Run once during setup:
  python backend/scripts/generate_default_assets.py
"""

from __future__ import annotations

import math
import os
import random
import struct
import sys
from pathlib import Path

SAMPLE_RATE = 44100


# ═══════════════════════════════════════════════════════════════════════════════
# WAV WRITER (pure Python, no dependencies)
# ═══════════════════════════════════════════════════════════════════════════════


def write_wav(
    filepath: str | Path,
    samples: list[float],
    sample_rate: int = SAMPLE_RATE,
    channels: int = 1,
    bits_per_sample: int = 16,
) -> None:
    """Write a list of float samples (range -1.0 … 1.0) to a 16-bit PCM WAV."""
    num_samples = len(samples)
    byte_rate = sample_rate * channels * (bits_per_sample // 8)
    block_align = channels * (bits_per_sample // 8)
    data_size = num_samples * block_align
    max_val = (2 ** (bits_per_sample - 1)) - 1

    with open(filepath, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        # fmt sub-chunk
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, channels, sample_rate, byte_rate, block_align, bits_per_sample))
        # data sub-chunk
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            f.write(struct.pack("<h", int(clamped * max_val)))


# ═══════════════════════════════════════════════════════════════════════════════
# SFX GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════


def generate_whoosh(duration: float = 0.5, sample_rate: int = SAMPLE_RATE) -> list[float]:
    """Cinematic transition whoosh — filtered noise with a frequency sweep."""
    n = int(duration * sample_rate)
    rng = random.Random(42)
    out: list[float] = []
    for i in range(n):
        t = i / sample_rate
        p = i / n  # 0 → 1 progress

        noise = rng.uniform(-1, 1)
        sweep = math.sin(p * math.pi)
        center_freq = 200 + sweep * 3000
        bp_mod = math.sin(2 * math.pi * center_freq * t)

        # attack / sustain / release envelope
        if p < 0.1:
            env = p / 0.1
        elif p > 0.7:
            env = (1.0 - p) / 0.3
        else:
            env = 1.0

        out.append(noise * bp_mod * env * 0.6)
    return out


def generate_riser(duration: float = 1.5, sample_rate: int = SAMPLE_RATE) -> list[float]:
    """Tension-building riser — exponentially rising pitch and volume."""
    n = int(duration * sample_rate)
    rng = random.Random(43)
    out: list[float] = []
    for i in range(n):
        t = i / sample_rate
        p = i / n

        freq = 100 * (2 ** (p * 4))
        nyquist = sample_rate / 2 - 100
        if freq > nyquist:
            freq = nyquist

        saw = 2.0 * (t * freq - math.floor(t * freq + 0.5))
        harmonic = math.sin(2 * math.pi * freq * 0.5 * t) * 0.3
        env = p ** 1.5
        noise = rng.uniform(-0.05, 0.05) * p

        s = (saw * 0.5 + harmonic + noise) * env * 0.7
        out.append(max(-1.0, min(1.0, s)))
    return out


def generate_bass_hit(duration: float = 0.4, sample_rate: int = SAMPLE_RATE) -> list[float]:
    """Punchy 808-style bass impact with transient click."""
    n = int(duration * sample_rate)
    rng = random.Random(44)
    out: list[float] = []
    for i in range(n):
        t = i / sample_rate
        p = i / n

        freq = 150 * math.exp(-p * 4) + 40
        sine = math.sin(2 * math.pi * freq * t)

        # sharp attack, exponential decay
        env = (p / 0.02) if p < 0.02 else math.exp(-(p - 0.02) * 8)

        # transient click for the first ~5 ms
        click = 0.0
        if p < 0.005:
            click = rng.uniform(-1, 1) * (1.0 - p / 0.005) * 0.8

        out.append(max(-1.0, min(1.0, sine * env * 0.9 + click)))
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# SYNTHWAVE LOOP GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════


def generate_synthwave_loop(
    duration: float = 16.0,
    bpm: float = 110.0,
    sample_rate: int = SAMPLE_RATE,
) -> list[float]:
    """
    Copyright-free synthwave/retrowave pulse loop.

    Layers: detuned saw-pad chord progression (Am → F → C → G),
    sub bass, 16th-note arpeggio, 4-on-the-floor kick, off-beat hi-hat,
    sidechain-style ducking envelope.
    """
    n = int(duration * sample_rate)
    beat_dur = 60.0 / bpm
    rng = random.Random(45)

    # chord voicings (Hz)
    chord_freqs = [
        [220.0, 261.63, 329.63],   # Am
        [174.61, 220.0, 261.63],   # F
        [261.63, 329.63, 392.0],   # C
        [196.0, 246.94, 293.66],   # G
    ]
    bass_notes = [110.0, 87.31, 130.81, 98.0]
    beats_per_chord = 4

    out: list[float] = []
    for i in range(n):
        t = i / sample_rate
        p = i / n

        beat = t / beat_dur
        chord_idx = int((beat / beats_per_chord) % len(chord_freqs))
        freqs = chord_freqs[chord_idx]
        bass_freq = bass_notes[chord_idx]

        # sidechain pump (4-on-the-floor)
        beat_phase = beat % 1.0
        sc = 0.3 + 0.7 * min(1.0, beat_phase * 3)

        # pad (detuned saw stack)
        pad = 0.0
        for f in freqs:
            for detune in (-1.5, 0.0, 1.5):
                pad += (2.0 * ((t * (f + detune)) % 1.0) - 1.0) * 0.08

        # sub bass
        bass = math.sin(2 * math.pi * bass_freq * t) * 0.35

        # arpeggio (16th notes)
        sixteenth = int(beat * 4) % len(freqs)
        arp_freq = freqs[sixteenth] * 2
        arp_env = max(0.0, 1.0 - ((beat * 4) % 1.0) * 2)
        arp = math.sin(2 * math.pi * arp_freq * t) * arp_env * 0.15

        # kick
        kick = 0.0
        if beat_phase < 0.15:
            kf = 150 * math.exp(-beat_phase * 30) + 45
            kick = math.sin(2 * math.pi * kf * beat_phase) * math.exp(-beat_phase * 15) * 0.5

        # hi-hat
        hihat = 0.0
        eighth_phase = (beat * 2) % 1.0
        if eighth_phase < 0.05:
            hihat = rng.uniform(-1, 1) * (1 - eighth_phase / 0.05) * 0.1

        mix = pad * sc + bass * sc + arp + kick + hihat

        # soft clip
        if mix > 0.9:
            mix = 0.9 + (mix - 0.9) * 0.1
        elif mix < -0.9:
            mix = -0.9 + (mix + 0.9) * 0.1

        # fade in/out for seamless loop
        if p < 0.01:
            mix *= p / 0.01
        elif p > 0.99:
            mix *= (1.0 - p) / 0.01

        out.append(max(-1.0, min(1.0, mix * 0.8)))

    return out


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> None:
    if len(sys.argv) > 1:
        base = Path(sys.argv[1])
    else:
        base = Path(__file__).resolve().parent.parent.parent  # scripts/ -> backend/ -> project root

    sfx_dir = base / "assets" / "sfx"
    music_dir = base / "assets" / "music"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    music_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 64)
    print("  VICECLIP STUDIO — Default Asset Generator")
    print("=" * 64)

    sfx_defs: list[tuple[str, str, object, dict]] = [
        ("whoosh.wav", "Cinematic Whoosh (0.5 s)", generate_whoosh, {"duration": 0.5}),
        ("riser.wav", "Tension Riser (1.5 s)", generate_riser, {"duration": 1.5}),
        ("bass_hit.wav", "808 Bass Hit (0.4 s)", generate_bass_hit, {"duration": 0.4}),
    ]

    for fname, label, gen_fn, kwargs in sfx_defs:
        fp = sfx_dir / fname
        if fp.exists():
            print(f"  [SKIP] {fp}")
            continue
        print(f"  [GEN]  {label}  →  {fp}")
        samples = gen_fn(sample_rate=SAMPLE_RATE, **kwargs)
        write_wav(fp, samples, sample_rate=SAMPLE_RATE)
        kb = fp.stat().st_size / 1024
        print(f"         {len(samples):,} samples  |  {kb:.1f} KB")

    loop_fp = music_dir / "default_synthwave_loop.wav"
    if loop_fp.exists():
        print(f"  [SKIP] {loop_fp}")
    else:
        print(f"  [GEN]  Synthwave Pulse Loop (16 s @ 110 BPM)  →  {loop_fp}")
        loop_samples = generate_synthwave_loop(duration=16.0, bpm=110.0, sample_rate=SAMPLE_RATE)
        write_wav(loop_fp, loop_samples, sample_rate=SAMPLE_RATE)
        kb = loop_fp.stat().st_size / 1024
        print(f"         {len(loop_samples):,} samples  |  {kb:.1f} KB")

    print()
    print(f"  SFX dir:   {sfx_dir}")
    print(f"  Music dir: {music_dir}")
    print("  ✔ All default assets ready.")
    print("=" * 64)


if __name__ == "__main__":
    main()
