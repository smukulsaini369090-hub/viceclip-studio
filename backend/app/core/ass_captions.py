"""
VICECLIP STUDIO — Animated ASS Subtitles & Top Hook Banner  (Pass 4 Stage E)
=============================================================================
Generates professional Advanced SubStation Alpha (.ass) subtitles for YouTube Shorts:
  1. Three signature GTA 6 themes:
     - `vice_city_neon`: Neon Cyan (&H00FFF000) base, Hot Pink (&H00932EFF) active word highlight.
     - `rockstar_bold`: High-voltage Rockstar Yellow (&H0000E6FF) with thick black outline.
     - `clean_minimal`: Crisp White (&H00FFFFFF) with translucent dark pill backdrop.
  2. Word-by-word active word highlighting:
     - 3-5 words per on-screen burst centered in lower-third (y ~ 1400 on 1080x1920 canvas).
     - Active spoken word scales up 115% with signature highlight color.
  3. 3-Second Top Curiosity Banner:
     - Prominently styled upper-screen banner (y ~ 180) during seconds 0.0 to 3.0.
     - Attention-grabbing curiosity frame to prevent scrolling.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.db.models import TranscriptSegment

logger = logging.getLogger("viceclip.captions")


@dataclass
class CaptionTheme:
    """Styling parameters for ASS subtitle render."""
    name: str
    font_name: str
    font_size: int
    primary_color: str    # ASS format &HAABBGGRR
    highlight_color: str  # ASS format &HAABBGGRR
    outline_color: str    # ASS format &HAABBGGRR
    back_color: str       # ASS format &HAABBGGRR
    outline_width: int
    shadow_depth: int
    bold: int
    banner_bg_color: str
    banner_text_color: str


# ASS Color Format: &H<Alpha><Blue><Green><Red> (Hex)
# Pink #FF2E93  -> R=FF, G=2E, B=93 -> &H00932EFF
# Cyan #00F0FF  -> R=00, G=F0, B=FF -> &H00FFF000
# Yellow #FFE600-> R=FF, G=E6, B=00 -> &H0000E6FF
# Dark Charcoal -> &H801A1A1A
THEMES: dict[str, CaptionTheme] = {
    "vice_city_neon": CaptionTheme(
        name="Vice City Neon",
        font_name="Arial Black",
        font_size=58,
        primary_color="&H00FFF000",      # Neon Cyan
        highlight_color="&H00932EFF",    # Vice Pink
        outline_color="&H00000000",      # Deep Black Outline
        back_color="&H60000000",         # Soft Black Shadow
        outline_width=5,
        shadow_depth=3,
        bold=1,
        banner_bg_color="&H00932EFF",    # Vice Pink
        banner_text_color="&H00FFFFFF",  # Pure White
    ),
    "rockstar_bold": CaptionTheme(
        name="Rockstar Bold",
        font_name="Impact",
        font_size=62,
        primary_color="&H0000E6FF",      # Rockstar Yellow
        highlight_color="&H00FFFFFF",    # Pure White
        outline_color="&H00000000",      # Thick Black
        back_color="&H80000000",
        outline_width=6,
        shadow_depth=4,
        bold=1,
        banner_bg_color="&H0000E6FF",    # Yellow
        banner_text_color="&H00000000",  # Black
    ),
    "clean_minimal": CaptionTheme(
        name="Clean Minimal",
        font_name="Trebuchet MS",
        font_size=54,
        primary_color="&H00FFFFFF",      # Crisp White
        highlight_color="&H0000F0FF",    # Cyan Pop
        outline_color="&H00151515",
        back_color="&H80000000",
        outline_width=4,
        shadow_depth=2,
        bold=1,
        banner_bg_color="&H00151515",    # Dark Matte
        banner_text_color="&H0000F0FF",  # Cyan Accent
    ),
}


def _format_ass_time(seconds: float) -> str:
    """Format seconds into ASS timestamp: H:MM:SS.cs"""
    seconds = max(0.0, seconds)
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    csecs = int(round((seconds - int(seconds)) * 100))
    if csecs >= 100:
        csecs = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{csecs:02d}"


def generate_ass_file(
    segments: list[TranscriptSegment],
    output_ass_path: str,
    top_banner_text: str = "",
    theme_name: str = "vice_city_neon",
    canvas_width: int = 1080,
    canvas_height: int = 1920,
    words_per_phrase: int = 4,
) -> str:
    """
    Assembles a complete, standards-compliant .ass subtitle script.
    """
    theme = THEMES.get(theme_name, THEMES["vice_city_neon"])
    out_file = Path(output_ass_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    header = f"""[Script Info]
Title: ViceClip Studio Dynamic Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: {canvas_width}
PlayResY: {canvas_height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{theme.font_name},{theme.font_size},{theme.primary_color},&H000000FF,{theme.outline_color},{theme.back_color},{theme.bold},0,0,0,100,100,1,0,1,{theme.outline_width},{theme.shadow_depth},2,60,60,420,1
Style: ActiveWord,{theme.font_name},{int(theme.font_size * 1.15)},{theme.highlight_color},&H000000FF,{theme.outline_color},{theme.back_color},{theme.bold},0,0,0,105,105,1,0,1,{theme.outline_width + 1},{theme.shadow_depth + 1},2,60,60,420,1
Style: TopBanner,Arial Black,46,{theme.banner_text_color},&H000000FF,&H00000000,{theme.banner_bg_color},1,0,0,0,100,100,2,0,3,10,0,8,40,40,160,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events: list[str] = []

    # 1. 3-Second Top Curiosity Banner
    if top_banner_text and top_banner_text.strip():
        banner_clean = top_banner_text.strip().upper()
        # Animated pop-in: scale from 80% to 100% in first 200ms
        banner_event = (
            f"Dialogue: 1,0:00:00.00,0:00:03.00,TopBanner,,0,0,0,,"
            f"{{\\fad(150,200)\\fscx85\\fscy85\\t(0,180,\\fscx100\\fscy100)}} {banner_clean} "
        )
        events.append(banner_event)

    # 2. Word-Level Spoken Captions with Active Highlight
    if segments:
        # Group segments into small rhythmic phrases (3-5 words)
        phrases: list[list[TranscriptSegment]] = []
        current_phrase: list[TranscriptSegment] = []

        for seg in segments:
            current_phrase.append(seg)
            if len(current_phrase) >= words_per_phrase or seg.text.endswith((".", "!", "?")):
                phrases.append(current_phrase)
                current_phrase = []

        if current_phrase:
            phrases.append(current_phrase)

        # Build active word events for each phrase
        for phrase in phrases:
            if not phrase:
                continue

            phrase_start = phrase[0].start
            phrase_end = phrase[-1].end

            # For each word in the phrase, render the phrase with that specific word highlighted
            for i, target_word in enumerate(phrase):
                w_start = _format_ass_time(target_word.start)
                w_end = _format_ass_time(target_word.end)

                text_parts: list[str] = []
                for j, word_seg in enumerate(phrase):
                    word_str = word_seg.text.upper()
                    if i == j:
                        # Highlighted active word
                        text_parts.append(f"{{\\c{theme.highlight_color}\\fscx112\\fscy112}}{word_str}{{\\r}}")
                    else:
                        # Inactive words
                        text_parts.append(f"{{\\c{theme.primary_color}}}{word_str}")

                rendered_phrase = " ".join(text_parts)
                events.append(f"Dialogue: 0,{w_start},{w_end},Default,,0,0,0,,{rendered_phrase}")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")

    logger.info("Generated ASS captions at %s (%d events, theme=%s)", out_file.name, len(events), theme_name)
    return str(out_file)
