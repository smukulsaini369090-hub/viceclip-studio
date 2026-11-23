"""
VICECLIP STUDIO — Gemini Brain  (Pass 2)
==========================================
Dual-mode Gemini integration:

1. **API Auto Mode** — Uses the official ``google-genai`` SDK
   (``from google import genai``) with configurable model selection
   and a "Test API Key & List Models" endpoint.

2. **Manual Copy-Paste Gemini Web Mode** — Zero-cost unlimited fallback
   where the app compiles the prompt, the user pastes it into
   ``gemini.google.com``, and copies the JSON response back.
   A bulletproof JSON extractor/sanitiser strips markdown fences,
   prose, and trailing commas before Pydantic validation.

All responses are validated against ``ViralBrainResponse`` (Pydantic v2).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

from app.config import get_settings
from app.core.prompt_builder import (
    build_commentary_script_prompt,
    build_viral_brain_prompt,
)
from app.db.models import (
    AudioSpike,
    ClipCandidate,
    GeminiTestResult,
    HeatmapPoint,
    TimestampedComment,
    TranscriptSegment,
    ViralBrainResponse,
    VisualSpike,
)

logger = logging.getLogger("viceclip.gemini")


# ═══════════════════════════════════════════════════════════════════════════════
# JSON SANITISER  (handles raw paste from gemini.google.com)
# ═══════════════════════════════════════════════════════════════════════════════

# Patterns for stripping markdown code fences
_FENCE_RE = re.compile(
    r"```(?:json|JSON|js|javascript)?\s*\n?(.*?)```",
    re.DOTALL,
)
# Fallback: find the outermost { ... } block
_BRACE_RE = re.compile(r"\{.*\}", re.DOTALL)
# Trailing comma before closing bracket/brace
_TRAILING_COMMA_RE = re.compile(r",\s*([}\]])")


def sanitise_gemini_json(raw: str) -> str:
    """
    Clean raw text pasted from Gemini Web into valid JSON.

    Handles:
      • Markdown fences (```json ... ```)
      • Prose before / after the JSON block
      • Multiple JSON blocks (takes the first valid one)
      • Trailing commas (non-standard but Gemini sometimes emits them)
      • Leading/trailing whitespace and BOM
    """
    # Strip BOM and whitespace
    text = raw.strip().lstrip("\ufeff")

    # 1. Try to extract from markdown fences
    fence_matches = _FENCE_RE.findall(text)
    candidates: list[str] = list(fence_matches)

    # 2. Try to extract outermost { ... }
    brace_match = _BRACE_RE.search(text)
    if brace_match:
        candidates.append(brace_match.group(0))

    # 3. Also try the raw text itself
    candidates.append(text)

    # Try each candidate
    for candidate in candidates:
        cleaned = candidate.strip()
        if not cleaned:
            continue

        # Remove trailing commas
        cleaned = _TRAILING_COMMA_RE.sub(r"\1", cleaned)

        # Attempt parse
        try:
            json.loads(cleaned)
            return cleaned
        except json.JSONDecodeError:
            continue

    # None of the candidates parsed — return the best-effort cleaned text
    # and let the caller handle the JSONDecodeError
    best = text
    if fence_matches:
        best = fence_matches[0].strip()
    elif brace_match:
        best = brace_match.group(0).strip()

    best = _TRAILING_COMMA_RE.sub(r"\1", best)
    return best


def parse_viral_brain_response(raw_json: str) -> ViralBrainResponse:
    """
    Parse and validate a raw JSON string (from API or manual paste)
    into a ``ViralBrainResponse``.

    Applies sanitisation first so direct pastes from Gemini Web work.
    """
    cleaned = sanitise_gemini_json(raw_json)
    data = json.loads(cleaned)
    return ViralBrainResponse.model_validate(data)


# ═══════════════════════════════════════════════════════════════════════════════
# GEMINI API CLIENT (google-genai SDK)
# ═══════════════════════════════════════════════════════════════════════════════


def _get_genai_client() -> object:
    """
    Create and return a configured ``google.genai.Client``.

    Uses the official ``google-genai`` package
    (``from google import genai`` — NOT the deprecated ``google-generativeai``).
    """
    from google import genai

    settings = get_settings()
    if not settings.gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Configure it in .env or use Manual Gemini Web Mode."
        )

    client = genai.Client(api_key=settings.gemini_api_key)
    return client


async def test_gemini_connection() -> GeminiTestResult:
    """
    Test the Gemini API key and list available models.
    Returns a ``GeminiTestResult`` for the Settings UI.
    """
    import asyncio

    settings = get_settings()

    if not settings.gemini_api_key:
        return GeminiTestResult(
            success=False,
            error="GEMINI_API_KEY is not set. Add it to .env or the Settings modal.",
        )

    try:
        from google import genai

        loop = asyncio.get_running_loop()

        def _test_sync() -> GeminiTestResult:
            client = genai.Client(api_key=settings.gemini_api_key)

            # List available models
            available: list[str] = []
            try:
                models_response = client.models.list()
                for model in models_response:
                    model_name = getattr(model, "name", str(model))
                    if isinstance(model_name, str):
                        available.append(model_name)
            except Exception as exc:
                logger.warning("Could not list models: %s", exc)

            # Test with a simple prompt
            test_model = settings.gemini_fast_model
            try:
                response = client.models.generate_content(
                    model=test_model,
                    contents="Respond with exactly: VICECLIP_OK",
                )
                preview = ""
                if hasattr(response, "text"):
                    preview = response.text[:200]
                elif hasattr(response, "candidates") and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                        for part in candidate.content.parts:
                            if hasattr(part, "text"):
                                preview += part.text
                        preview = preview[:200]

                return GeminiTestResult(
                    success=True,
                    model_name=test_model,
                    available_models=available,
                    response_preview=preview.strip(),
                )
            except Exception as exc:
                return GeminiTestResult(
                    success=False,
                    model_name=test_model,
                    available_models=available,
                    error=f"Model test failed: {exc}",
                )

        return await loop.run_in_executor(None, _test_sync)

    except ImportError:
        return GeminiTestResult(
            success=False,
            error="google-genai package not installed. Run: pip install google-genai",
        )
    except Exception as exc:
        return GeminiTestResult(success=False, error=str(exc))


async def run_viral_brain_api(
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
    model_override: Optional[str] = None,
) -> ViralBrainResponse:
    """
    Run the Viral Brain via the Gemini API (Auto Mode).

    Builds the prompt, sends it to the configured deep model,
    sanitises the response, and validates via Pydantic.
    """
    import asyncio

    settings = get_settings()
    model = model_override or settings.gemini_deep_model

    prompt = build_viral_brain_prompt(
        video_title=video_title,
        video_channel=video_channel,
        video_duration_sec=video_duration_sec,
        transcript_segments=transcript_segments,
        heatmap=heatmap,
        comments=comments,
        audio_spikes=audio_spikes,
        visual_spikes=visual_spikes,
        retention_vault_winners=retention_vault_winners,
    )

    logger.info("Sending Viral Brain prompt to Gemini API (model=%s, prompt_len=%d)", model, len(prompt))

    loop = asyncio.get_running_loop()

    def _call_sync() -> str:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": 0.7,
                "max_output_tokens": 8192,
            },
        )

        raw_text = ""
        if hasattr(response, "text"):
            raw_text = response.text
        elif hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if hasattr(part, "text"):
                        raw_text += part.text

        if not raw_text.strip():
            raise RuntimeError("Gemini returned an empty response")

        return raw_text

    raw_response = await loop.run_in_executor(None, _call_sync)

    logger.info("Gemini API response received (%d chars)", len(raw_response))
    result = parse_viral_brain_response(raw_response)
    logger.info("Viral Brain returned %d clip candidates", len(result.clips))

    return result


async def run_commentary_api(
    *,
    clip_title: str,
    clip_transcript: str,
    clip_duration_sec: float,
    video_title: str,
    model_override: Optional[str] = None,
) -> str:
    """
    Generate a transformative commentary script via Gemini API.
    Returns plain text script (not JSON).
    """
    import asyncio

    settings = get_settings()
    model = model_override or settings.gemini_fast_model

    prompt = build_commentary_script_prompt(
        clip_title=clip_title,
        clip_transcript=clip_transcript,
        clip_duration_sec=clip_duration_sec,
        video_title=video_title,
    )

    logger.info("Generating commentary script via Gemini (model=%s)", model)

    loop = asyncio.get_running_loop()

    def _call_sync() -> str:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": 0.8,
                "max_output_tokens": 2048,
            },
        )

        text = ""
        if hasattr(response, "text"):
            text = response.text
        elif hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if hasattr(part, "text"):
                        text += part.text

        return text.strip()

    script = await loop.run_in_executor(None, _call_sync)
    logger.info("Commentary script generated (%d chars)", len(script))
    return script


# ═══════════════════════════════════════════════════════════════════════════════
# MANUAL COPY-PASTE GEMINI WEB MODE
# ═══════════════════════════════════════════════════════════════════════════════


def get_manual_prompt(
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
) -> str:
    """
    Build and return the full prompt for Manual Copy-Paste mode.

    The user copies this prompt, pastes it into ``gemini.google.com``,
    and copies the JSON response back into VICECLIP STUDIO.
    """
    return build_viral_brain_prompt(
        video_title=video_title,
        video_channel=video_channel,
        video_duration_sec=video_duration_sec,
        transcript_segments=transcript_segments,
        heatmap=heatmap,
        comments=comments,
        audio_spikes=audio_spikes,
        visual_spikes=visual_spikes,
        retention_vault_winners=retention_vault_winners,
    )


def parse_manual_response(pasted_text: str) -> ViralBrainResponse:
    """
    Parse a user-pasted response from Gemini Web.

    Automatically handles:
      • Markdown fences (```json ... ```)
      • Extra prose before/after JSON
      • Trailing commas
      • Unicode BOM

    Raises ``json.JSONDecodeError`` or ``pydantic.ValidationError``
    with clear error messages if the paste is invalid.
    """
    return parse_viral_brain_response(pasted_text)


def get_manual_commentary_prompt(
    *,
    clip_title: str,
    clip_transcript: str,
    clip_duration_sec: float,
    video_title: str,
) -> str:
    """
    Build and return the commentary script prompt for Manual mode.
    """
    return build_commentary_script_prompt(
        clip_title=clip_title,
        clip_transcript=clip_transcript,
        clip_duration_sec=clip_duration_sec,
        video_title=video_title,
    )
