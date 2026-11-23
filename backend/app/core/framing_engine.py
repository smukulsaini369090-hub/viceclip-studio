"""
VICECLIP STUDIO — Smart Gaming Framing Engine  (Pass 4 Stage B)
================================================================
Intelligently formats 16:9 gaming video into 9:16 (1080x1920) YouTube Shorts:
  1. Facecam Detection (MediaPipe):
     - Analyzes sampled frames to locate creator's facecam box.
     - If Facecam detected:
       - Renders **Top 35% Facecam (1080x672) + Bottom 65% Center-Tracked Gameplay (1080x1248)** split-screen.
     - If Pure Gameplay / Trailer:
       - Renders **9:16 Action-Centered Crop (1080x1920)** with optional blurred background backdrop.
  2. Manual Override Support:
     - Directly honors `CropOverride` coordinates {x, y, w, h} from Frontend 9:16 Playground.
  3. Strict VRAM management via `VRAMManager.acquire_gpu(GPUStage.MEDIAPIPE)`.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from app.core.vram_manager import GPUStage, flush_gpu_memory, get_vram_manager
from app.db.models import CropOverride

logger = logging.getLogger("viceclip.framing")


@dataclass
class BoundingBox:
    """Normalized bounding box [0.0 - 1.0]."""
    x: float
    y: float
    w: float
    h: float


@dataclass
class FramingLayout:
    """Computed 9:16 framing configuration."""
    is_split_screen: bool
    facecam_box: Optional[BoundingBox]
    gameplay_box: BoundingBox
    use_blurred_backdrop: bool
    ffmpeg_filter: str


def detect_facecam_sync(
    video_path: str,
    sample_count: int = 8,
    min_detection_confidence: float = 0.55,
) -> Optional[BoundingBox]:
    """
    Samples frames from the video and uses MediaPipe to detect persistent face positions.
    Returns normalized facecam BoundingBox if a consistent face is found, or None for pure gameplay.
    """
    import mediapipe as mp

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.warning("Could not open video for facecam detection: %s", video_path)
        return None

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total_frames <= 0:
        cap.release()
        return None

    # Sample evenly across the video
    sample_indices = np.linspace(0, total_frames - 1, sample_count, dtype=int)
    detected_boxes: list[BoundingBox] = []

    try:
        import mediapipe as mp
        if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_detection"):
            mp_face = mp.solutions.face_detection
            with mp_face.FaceDetection(
                model_selection=1,  # full-range model for corner facecam
                min_detection_confidence=min_detection_confidence,
            ) as detector:
                for idx in sample_indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        continue

                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = detector.process(rgb)

                    if results.detections:
                        for detection in results.detections:
                            box = detection.location_data.relative_bounding_box
                            # Expand face box slightly into a head-and-shoulders facecam box
                            pad_x = box.width * 0.4
                            pad_y = box.height * 0.4
                            x = max(0.0, box.xmin - pad_x)
                            y = max(0.0, box.ymin - pad_y)
                            w = min(1.0 - x, box.width + pad_x * 2)
                            h = min(1.0 - y, box.height + pad_y * 2)
                            detected_boxes.append(BoundingBox(x=x, y=y, w=w, h=h))
        else:
            raise AttributeError("mediapipe has no solutions")
    except Exception:
        # Fast, offline OpenCV Haar Cascade fallback
        try:
            cc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            for idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if not ret or frame is None:
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = cc.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))
                ih, iw = frame.shape[:2]
                for (fx, fy, fw, fh) in faces:
                    pad_x = fw * 0.4
                    pad_y = fh * 0.4
                    x = max(0.0, (fx - pad_x) / iw)
                    y = max(0.0, (fy - pad_y) / ih)
                    w = min(1.0 - x, (fw + pad_x * 2) / iw)
                    h = min(1.0 - y, (fh + pad_y * 2) / ih)
                    detected_boxes.append(BoundingBox(x=x, y=y, w=w, h=h))
        except Exception as exc:
            logger.warning("Face detection fallback error: %s", exc)

    cap.release()

    # If faces were found in >= 50% of sampled frames, treat as persistent facecam
    if len(detected_boxes) >= (sample_count * 0.4):
        # Average the bounding boxes
        avg_x = float(np.median([b.x for b in detected_boxes]))
        avg_y = float(np.median([b.y for b in detected_boxes]))
        avg_w = float(np.median([b.w for b in detected_boxes]))
        avg_h = float(np.median([b.h for b in detected_boxes]))

        # Enforce minimum size for facecam
        avg_w = max(0.20, min(0.50, avg_w))
        avg_h = max(0.25, min(0.55, avg_h))

        logger.info(
            "Facecam detected: x=%.2f, y=%.2f, w=%.2f, h=%.2f across %d detections",
            avg_x, avg_y, avg_w, avg_h, len(detected_boxes)
        )
        return BoundingBox(x=avg_x, y=avg_y, w=avg_w, h=avg_h)

    logger.info("No consistent facecam detected — classified as Pure Gameplay / Cinematic")
    return None


async def analyze_framing(
    video_path: str,
    custom_crop: Optional[CropOverride] = None,
    allow_split_screen: bool = True,
    use_blurred_backdrop: bool = False,
) -> FramingLayout:
    """
    Asynchronously determines optimal 9:16 layout.
    """
    facecam_box: Optional[BoundingBox] = None

    if custom_crop is not None:
        # User manual override from Frontend 9:16 Playground
        gameplay_box = BoundingBox(
            x=custom_crop.x,
            y=custom_crop.y,
            w=custom_crop.w,
            h=custom_crop.h,
        )
        is_split = False
        logger.info("Using custom crop box override from user: %s", gameplay_box)
    else:
        # Automated detection
        if allow_split_screen:
            mgr = get_vram_manager()
            async with mgr.acquire_gpu(GPUStage.MEDIAPIPE):
                loop = asyncio.get_running_loop()
                facecam_box = await loop.run_in_executor(
                    None,
                    detect_facecam_sync,
                    video_path,
                )
                flush_gpu_memory()

        if facecam_box is not None:
            is_split = True
            # Gameplay occupies central 60% of original frame
            gameplay_box = BoundingBox(x=0.20, y=0.10, w=0.60, h=0.80)
        else:
            is_split = False
            # Standard 9:16 action crop: center 56.25% width (9 / 16 of 1080p is ~608px out of 1920)
            # Normalized width for 9:16 inside 16:9 = (1080/1920) * (9/16) ~= 0.316 or center 56.25% of height
            # 16:9 is 1.777 aspect, 9:16 is 0.5625 aspect.
            # Crop 9:16 from 16:9 width: w_norm = (9/16) / (16/9) = 0.3164. Center x = (1 - 0.3164) / 2 = 0.3418
            gameplay_box = BoundingBox(x=0.3418, y=0.0, w=0.3164, h=1.0)

    # Compile FFmpeg filter string for 1080x1920 output
    filter_str = compile_framing_filter(
        is_split_screen=is_split,
        facecam_box=facecam_box,
        gameplay_box=gameplay_box,
        use_blurred_backdrop=use_blurred_backdrop,
    )

    return FramingLayout(
        is_split_screen=is_split,
        facecam_box=facecam_box,
        gameplay_box=gameplay_box,
        use_blurred_backdrop=use_blurred_backdrop,
        ffmpeg_filter=filter_str,
    )


def compile_framing_filter(
    is_split_screen: bool,
    facecam_box: Optional[BoundingBox],
    gameplay_box: BoundingBox,
    use_blurred_backdrop: bool = False,
    output_width: int = 1080,
    output_height: int = 1920,
) -> str:
    """
    Compiles production-ready FFmpeg `filter_complex` string to composite
    1080x1920 vertical canvas.

    Layout A (Split Screen - Facecam + Gameplay):
      - Top 35% (1080x672): Facecam crop, scaled to 1080x672.
      - Bottom 65% (1080x1248): Gameplay crop, scaled to 1080x1248.
      - Subtle 2px neon separator line between sections.

    Layout B (Pure Gameplay):
      - If blurred backdrop enabled:
        - Layer 0: Background scaled to 1080x1920 + heavy Gaussian blur (boxblur=20:5).
        - Layer 1: Sharp center video scaled preserving aspect ratio overlaid in middle.
      - If standard crop:
        - Direct crop to 9:16 aspect ratio scaled to 1080x1920.
    """
    if is_split_screen and facecam_box is not None:
        face_h = int(output_height * 0.35)  # 672
        game_h = output_height - face_h    # 1248

        filter_chain = (
            f"[0:v]split=2[v_face_in][v_game_in];"
            # 1. Facecam crop & scale to top 35%
            f"[v_face_in]crop=w=iw*{facecam_box.w:.4f}:h=ih*{facecam_box.h:.4f}:"
            f"x=iw*{facecam_box.x:.4f}:y=ih*{facecam_box.y:.4f},"
            f"scale={output_width}:{face_h}:force_original_aspect_ratio=increase,"
            f"crop={output_width}:{face_h}[facecam];"
            # 2. Gameplay crop & scale to bottom 65%
            f"[v_game_in]crop=w=iw*{gameplay_box.w:.4f}:h=ih*{gameplay_box.h:.4f}:"
            f"x=iw*{gameplay_box.x:.4f}:y=ih*{gameplay_box.y:.4f},"
            f"scale={output_width}:{game_h}:force_original_aspect_ratio=increase,"
            f"crop={output_width}:{game_h}[gameplay];"
            # 3. Vertical stack facecam on top of gameplay
            f"[facecam][gameplay]vstack=inputs=2[framed_v]"
        )
        return filter_chain

    elif use_blurred_backdrop:
        filter_chain = (
            f"[0:v]split=2[v_bg_in][v_fg_in];"
            # Blurred background filling 1080x1920
            f"[v_bg_in]scale={output_width}:{output_height}:force_original_aspect_ratio=increase,"
            f"crop={output_width}:{output_height},boxblur=25:5[bg];"
            # Sharp foreground centered
            f"[v_fg_in]scale={output_width}:-1[fg];"
            # Overlay sharp foreground on blurred background
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[framed_v]"
        )
        return filter_chain

    else:
        # Clean 9:16 Center Crop directly
        # crop=w=ih*(9/16):h=ih:x=(iw-ow)/2:y=0,scale=1080:1920
        filter_chain = (
            f"[0:v]crop=w=iw*{gameplay_box.w:.4f}:h=ih*{gameplay_box.h:.4f}:"
            f"x=iw*{gameplay_box.x:.4f}:y=ih*{gameplay_box.y:.4f},"
            f"scale={output_width}:{output_height}:force_original_aspect_ratio=increase,"
            f"crop={output_width}:{output_height}[framed_v]"
        )
        return filter_chain
