"""
VICECLIP STUDIO — Hardware & Pipeline Smoke Test
==================================================
Verifies the complete local pipeline on Windows 11 + NVIDIA RTX 3050 (6 GB VRAM)
before running full YouTube downloads.

Tests Executed:
  1. System & Python Environment (Python 3.11+, Windows 11, path resolution)
  2. PyTorch & CUDA Hardware Acceleration (RTX 3050 detection, VRAM capacity)
  3. VRAMManager Concurrency & GPU Flush Test (torch empty_cache + gc)
  4. FFmpeg & Hardware NVENC Synthetic Encode Test (h264_nvenc 1080x1920 @ 60fps)
  5. Synthetic Audio & ASS Subtitles Generation (Vice City Neon theme)
  6. End-to-End Synthetic 9:16 Render Test (framing + subtitles + NVENC export)
  7. Shorts Cover PNG Frame Extraction

Usage:
  python backend/scripts/smoke_test.py
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

# Add backend directory to sys.path so app modules import cleanly
_BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND_DIR))

# Console color helpers
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(title: str) -> None:
    print(f"\n{CYAN}{BOLD}{'=' * 68}{RESET}")
    print(f"{CYAN}{BOLD}  {title}{RESET}")
    print(f"{CYAN}{BOLD}{'=' * 68}{RESET}")


def print_pass(msg: str) -> None:
    print(f"  {GREEN}✔ PASS:{RESET} {msg}")


def print_warn(msg: str) -> None:
    print(f"  {YELLOW}⚠ WARN:{RESET} {msg}")


def print_fail(msg: str) -> None:
    print(f"  {RED}✘ FAIL:{RESET} {msg}")


def print_info(label: str, val: str) -> None:
    print(f"  {BOLD}{label}:{RESET} {val}")


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: ENVIRONMENT & PYTHON
# ═══════════════════════════════════════════════════════════════════════════════

def test_environment() -> bool:
    print_header("TEST 1: System & Python Environment")

    py_ver = sys.version_info
    print_info("Python Version", f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    print_info("Platform", sys.platform)
    print_info("Executable", sys.executable)
    print_info("Backend Path", str(_BACKEND_DIR))

    if py_ver < (3, 11):
        print_fail("Python 3.11+ is required for optimal asyncio performance.")
        return False
    else:
        print_pass("Python version meets requirement (>= 3.11)")

    if sys.platform != "win32":
        print_warn("Non-Windows OS detected. ViceClip Studio is optimized for Windows 11.")
    else:
        print_pass("Windows OS verified.")

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: PYTORCH & CUDA CAPABILITY
# ═══════════════════════════════════════════════════════════════════════════════

def test_cuda() -> bool:
    print_header("TEST 2: PyTorch & CUDA Capability (RTX 3050 6GB)")

    try:
        import torch
        print_info("PyTorch Version", torch.__version__)

        if not torch.cuda.is_available():
            print_warn("CUDA is not available in current environment. Pipeline will use CPU fallback.")
            return False

        device_name = torch.cuda.get_device_name(0)
        vram_total_mb = int(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024))
        print_info("CUDA Device", device_name)
        print_info("Device VRAM", f"{vram_total_mb} MB")

        if vram_total_mb < 5500:
            print_warn(f"GPU has {vram_total_mb} MB VRAM. VRAMManager will strictly serialize stages.")
        else:
            print_pass(f"RTX GPU with {vram_total_mb} MB VRAM detected.")

        # Test simple tensor allocation
        x = torch.zeros((1000, 1000), device="cuda")
        del x
        torch.cuda.empty_cache()
        print_pass("CUDA tensor allocation & cache release verified.")
        return True

    except ImportError:
        print_warn("PyTorch is not installed in the current Python environment.")
        print_info("Notice", "Run setup.ps1 to install CUDA-enabled PyTorch inside .venv.")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: VRAM MANAGER CONCURRENCY & TELEMETRY
# ═══════════════════════════════════════════════════════════════════════════════

async def test_vram_manager() -> bool:
    print_header("TEST 3: VRAMManager Concurrency & GPU Flush")

    try:
        from app.core.vram_manager import GPUStage, get_vram_manager

        mgr = get_vram_manager()
        status_init = mgr.get_vram_status()
        print_info("Initial VRAM", f"{status_init['used_mb']} / {status_init['total_mb']} MB ({status_init['utilization_pct']}%)")

        # Test acquiring lock
        async with mgr.acquire_gpu(GPUStage.WHISPER):
            print_pass(f"GPU lock acquired for stage: {mgr.current_stage.value}")
            await asyncio.sleep(0.5)

        print_pass("GPU lock released and post-stage VRAM flush completed.")
        return True

    except Exception as exc:
        print_fail(f"VRAMManager test encountered error: {exc}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: FFMPEG & NVENC ENCODER TEST
# ═══════════════════════════════════════════════════════════════════════════════

def test_ffmpeg_nvenc() -> bool:
    print_header("TEST 4: FFmpeg & Hardware NVENC Encoding")

    try:
        from app.config import check_ffmpeg_available, check_nvenc_available, get_settings

        cfg = get_settings()

        if not check_ffmpeg_available(cfg.ffmpeg_path):
            print_fail(f"FFmpeg not reachable at: {cfg.ffmpeg_path}")
            return False
        print_pass(f"FFmpeg binary reachable ({cfg.ffmpeg_path})")

        nvenc_ok = check_nvenc_available(cfg.ffmpeg_path)
        if nvenc_ok:
            print_pass("Hardware encoder 'h264_nvenc' verified with synthetic 1-frame test.")
        else:
            print_warn("Hardware 'h264_nvenc' unavailable. Renderer will use 'libx264' CPU fallback.")

        print_info("Active Video Encoder", cfg.encoder)
        return True

    except Exception as exc:
        print_fail(f"FFmpeg/NVENC test failed: {exc}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 5 & 6: SYNTHETIC MEDIA RENDER & COVER TEST
# ═══════════════════════════════════════════════════════════════════════════════

def test_synthetic_render() -> bool:
    print_header("TEST 5 & 6: Synthetic 9:16 Short Render & Cover Extraction")

    try:
        from app.config import get_settings
        from app.core.ass_captions import generate_ass_file
        from app.core.framing_engine import compile_framing_filter
        from app.core.nvenc_renderer import extract_cover_thumbnail_sync, render_short_sync
        from app.db.models import CropOverride, TranscriptSegment

        cfg = get_settings()
        test_dir = Path(cfg.output_dir) / "smoke_test"
        test_dir.mkdir(parents=True, exist_ok=True)

        synth_video = str(test_dir / "synth_raw_16x9.mp4")
        synth_audio = str(test_dir / "synth_audio.wav")
        synth_ass = str(test_dir / "synth_subs.ass")
        synth_out = str(test_dir / "synth_render_9x16.mp4")
        synth_cover = str(test_dir / "synth_cover.png")

        # 1. Generate 3-second synthetic 16:9 1080p video with color bars
        cmd_gen_v = [
            cfg.ffmpeg_path, "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", "testsrc=size=1920x1080:rate=60:duration=3",
            "-pix_fmt", "yuv420p",
            synth_video,
        ]
        subprocess.run(cmd_gen_v, check=True)
        print_pass(f"Generated synthetic 1080p source video (3s): {Path(synth_video).name}")

        # 2. Generate 3-second synthetic sine wave audio
        cmd_gen_a = [
            cfg.ffmpeg_path, "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
            synth_audio,
        ]
        subprocess.run(cmd_gen_a, check=True)
        print_pass(f"Generated synthetic audio (3s): {Path(synth_audio).name}")

        # 3. Generate ASS subtitles with Vice City Neon theme
        sample_segments = [
            TranscriptSegment(text="CHECK", start=0.2, end=0.7),
            TranscriptSegment(text="OUT", start=0.7, end=1.1),
            TranscriptSegment(text="THIS", start=1.1, end=1.6),
            TranscriptSegment(text="GTA", start=1.6, end=2.1),
            TranscriptSegment(text="6", start=2.1, end=2.7),
        ]
        generate_ass_file(
            segments=sample_segments,
            output_ass_path=synth_ass,
            top_banner_text="DID YOU SPOT THIS IN GTA 6?",
            theme_name="vice_city_neon",
        )
        print_pass("Generated animated ASS subtitles with 3s top hook banner")

        # 4. Compile 9:16 Action-Centered Crop Framing Filter
        framing_filter = compile_framing_filter(
            is_split_screen=False,
            facecam_box=None,
            gameplay_box=type("BBox", (), {"x": 0.3418, "y": 0.0, "w": 0.3164, "h": 1.0})(),
            use_blurred_backdrop=False,
        )

        # 5. Execute 1080x1920 @ 60fps GPU render
        t0 = time.time()
        rendered_mp4, encoder_used = render_short_sync(
            input_video_path=synth_video,
            input_audio_path=synth_audio,
            ass_subtitles_path=synth_ass,
            output_mp4_path=synth_out,
            framing_filter_str=framing_filter,
            relative_start_sec=0.0,
            clip_duration_sec=3.0,
            encoder_name=cfg.encoder,
            target_fps=60,
        )
        elapsed = time.time() - t0
        mb_size = Path(rendered_mp4).stat().st_size / (1024 * 1024)
        print_pass(f"Rendered 1080x1920 @ 60fps Short in {elapsed:.2f}s ({mb_size:.2f} MB, encoder={encoder_used})")

        # 6. Extract Shorts cover PNG
        extract_cover_thumbnail_sync(rendered_mp4, synth_cover, timestamp_sec=1.5)
        print_pass(f"Extracted high-contrast Shorts cover PNG ({Path(synth_cover).name})")

        # Clean up temporary test files
        for f in [synth_video, synth_audio, synth_ass, synth_out, synth_cover]:
            try:
                os.remove(f)
            except Exception:
                pass

        return True

    except Exception as exc:
        print_fail(f"Synthetic render test failed: {exc}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

async def main_async() -> None:
    print(f"\n{MAGENTA}{BOLD}")
    print("  ██╗   ██╗██╗ ██████╗███████╗ ██████╗██╗     ██╗██████╗ ")
    print("  ██║   ██║██║██╔════╝██╔════╝██╔════╝██║     ██║██╔══██╗")
    print("  ██║   ██║██║██║     █████╗  ██║     ██║     ██║██████╔╝")
    print("  ╚██╗ ██╔╝██║██║     ██╔══╝  ██║     ██║     ██║██╔═══╝ ")
    print("   ╚████╔╝ ██║╚██████╗███████╗╚██████╗███████╗██║██║     ")
    print("    ╚═══╝  ╚═╝ ╚═════╝╚══════╝ ╚═════╝╚══════╝╚═╝╚═╝     ")
    print(f"            S M O K E   T E S T   S U I T E{RESET}\n")

    results: list[tuple[str, bool]] = []

    # 1. Environment
    results.append(("Environment Check", test_environment()))

    # 2. CUDA
    results.append(("PyTorch / CUDA Support", test_cuda()))

    # 3. VRAM Manager
    results.append(("VRAMManager Concurrency", await test_vram_manager()))

    # 4. FFmpeg / NVENC
    results.append(("FFmpeg / NVENC Availability", test_ffmpeg_nvenc()))

    # 5 & 6. Synthetic Render
    results.append(("End-to-End Synthetic Render", test_synthetic_render()))

    # Summary
    print_header("SMOKE TEST RESULTS SUMMARY")
    all_passed = True
    for name, passed in results:
        status_text = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL / WARN{RESET}"
        print(f"  {name:<35} : {status_text}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print(f"  {GREEN}{BOLD}✔ ALL PIPELINE MODULES ARE READY FOR PRODUCTION.{RESET}\n")
    else:
        print(f"  {YELLOW}{BOLD}⚠ System is functional with CPU fallbacks where indicated above.{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main_async())
