"""
VICECLIP STUDIO — SQLite Database Manager
===========================================
Async SQLite via ``aiosqlite`` for:
  • Smart Cache (video metadata, transcripts, heatmaps, signals)
  • Clip Candidates (Viral Brain output with virality scores)
  • Retention Vault (post-upload AVD / view metrics for self-learning)
  • Job Queue (batch watchlist processing)

All tables are created on first connection (idempotent).
WAL journal mode is enabled for concurrent reads during renders.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import aiosqlite

from app.config import get_settings

logger = logging.getLogger("viceclip.db")

_db_connection: Optional[aiosqlite.Connection] = None


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA DDL
# ═══════════════════════════════════════════════════════════════════════════════

_SCHEMA_SQL = """
-- ─── Smart Cache ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS video_cache (
    video_id          TEXT PRIMARY KEY,
    url               TEXT    NOT NULL,
    title             TEXT    NOT NULL DEFAULT '',
    channel           TEXT    NOT NULL DEFAULT '',
    duration_sec      REAL    NOT NULL DEFAULT 0,
    thumbnail_url     TEXT    NOT NULL DEFAULT '',
    transcript_json   TEXT    NOT NULL DEFAULT '[]',
    heatmap_json      TEXT    NOT NULL DEFAULT '[]',
    comments_json     TEXT    NOT NULL DEFAULT '[]',
    audio_spikes_json TEXT    NOT NULL DEFAULT '[]',
    visual_spikes_json TEXT   NOT NULL DEFAULT '[]',
    download_path     TEXT    NOT NULL DEFAULT '',
    audio_path        TEXT    NOT NULL DEFAULT '',
    created_at        TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ─── Clip Candidates ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clip_candidates (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id                TEXT    NOT NULL,
    clip_id                 TEXT    NOT NULL,
    rank                    INTEGER NOT NULL DEFAULT 0,
    title_hook              TEXT    NOT NULL DEFAULT '',
    start_sec               REAL    NOT NULL,
    end_sec                 REAL    NOT NULL,
    virality_score          REAL    NOT NULL DEFAULT 0,
    score_visual_hook       REAL    NOT NULL DEFAULT 0,
    score_replay_loop       REAL    NOT NULL DEFAULT 0,
    score_debate_bait       REAL    NOT NULL DEFAULT 0,
    score_payoff_speed      REAL    NOT NULL DEFAULT 0,
    banner_text_a           TEXT    NOT NULL DEFAULT '',
    banner_text_b           TEXT    NOT NULL DEFAULT '',
    needs_easter_egg_zoom   INTEGER NOT NULL DEFAULT 0,
    easter_egg_description  TEXT    NOT NULL DEFAULT '',
    upload_kit_json         TEXT    NOT NULL DEFAULT '{}',
    gemini_raw_json         TEXT    NOT NULL DEFAULT '{}',
    status                  TEXT    NOT NULL DEFAULT 'pending',
    output_path_a           TEXT    NOT NULL DEFAULT '',
    output_path_b           TEXT    NOT NULL DEFAULT '',
    cover_path              TEXT    NOT NULL DEFAULT '',
    created_at              TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (video_id) REFERENCES video_cache(video_id) ON DELETE CASCADE
);

-- ─── Retention Vault ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS retention_vault (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    clip_id         TEXT    NOT NULL,
    video_id        TEXT    NOT NULL,
    title_hook      TEXT    NOT NULL DEFAULT '',
    views_48h       INTEGER NOT NULL DEFAULT 0,
    avd_pct         REAL    NOT NULL DEFAULT 0,
    viewed_pct      REAL    NOT NULL DEFAULT 0,
    swiped_pct      REAL    NOT NULL DEFAULT 0,
    hook_formula    TEXT    NOT NULL DEFAULT '',
    clip_pattern    TEXT    NOT NULL DEFAULT '',
    banner_text     TEXT    NOT NULL DEFAULT '',
    notes           TEXT    NOT NULL DEFAULT '',
    logged_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (video_id) REFERENCES video_cache(video_id) ON DELETE CASCADE
);

-- ─── Job Queue ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_queue (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    video_url       TEXT    NOT NULL,
    video_id        TEXT    NOT NULL DEFAULT '',
    status          TEXT    NOT NULL DEFAULT 'queued',
    priority        INTEGER NOT NULL DEFAULT 0,
    settings_json   TEXT    NOT NULL DEFAULT '{}',
    progress_pct    REAL    NOT NULL DEFAULT 0,
    current_stage   TEXT    NOT NULL DEFAULT '',
    error_message   TEXT    NOT NULL DEFAULT '',
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    started_at      TEXT,
    completed_at    TEXT
);

-- ─── Indexes ────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_clip_video   ON clip_candidates(video_id);
CREATE INDEX IF NOT EXISTS idx_clip_status  ON clip_candidates(status);
CREATE INDEX IF NOT EXISTS idx_retention_avd ON retention_vault(avd_pct DESC);
CREATE INDEX IF NOT EXISTS idx_job_status   ON job_queue(status, priority DESC);
"""


# ═══════════════════════════════════════════════════════════════════════════════
# CONNECTION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════


async def get_db() -> aiosqlite.Connection:
    """Return (or create) the singleton async database connection."""
    global _db_connection

    if _db_connection is not None:
        try:
            await _db_connection.execute("SELECT 1")
            return _db_connection
        except Exception:
            _db_connection = None

    settings = get_settings()
    db_path = settings.db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Opening SQLite database: %s", db_path)
    _db_connection = await aiosqlite.connect(str(db_path))
    _db_connection.row_factory = aiosqlite.Row

    await _db_connection.execute("PRAGMA journal_mode=WAL")
    await _db_connection.execute("PRAGMA foreign_keys=ON")
    await _db_connection.executescript(_SCHEMA_SQL)
    await _db_connection.commit()

    logger.info("Database ready — all tables created")
    return _db_connection


async def close_db() -> None:
    """Cleanly close the database connection."""
    global _db_connection
    if _db_connection is not None:
        await _db_connection.close()
        _db_connection = None
        logger.info("Database connection closed")


# ═══════════════════════════════════════════════════════════════════════════════
# SMART CACHE CRUD
# ═══════════════════════════════════════════════════════════════════════════════


async def cache_get_video(video_id: str) -> Optional[dict]:
    """Retrieve a cached video analysis by normalised video ID."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM video_cache WHERE video_id = ?", (video_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def cache_upsert_video(video_id: str, data: dict) -> None:
    """Insert or update a video cache entry (upsert on video_id conflict)."""
    db = await get_db()

    columns = [
        "video_id", "url", "title", "channel", "duration_sec", "thumbnail_url",
        "transcript_json", "heatmap_json", "comments_json",
        "audio_spikes_json", "visual_spikes_json",
        "download_path", "audio_path",
    ]
    values: list[object] = []
    for col in columns:
        if col == "video_id":
            values.append(video_id)
        elif col.endswith("_json"):
            raw = data.get(col, data.get(col.replace("_json", ""), []))
            values.append(json.dumps(raw) if not isinstance(raw, str) else raw)
        else:
            values.append(data.get(col, ""))

    placeholders = ", ".join(["?"] * len(columns))
    col_names = ", ".join(columns)
    update_set = ", ".join(
        f"{c} = excluded.{c}" for c in columns if c != "video_id"
    )
    update_set += ", updated_at = datetime('now')"

    sql = (
        f"INSERT INTO video_cache ({col_names}) VALUES ({placeholders}) "
        f"ON CONFLICT(video_id) DO UPDATE SET {update_set}"
    )
    await db.execute(sql, values)
    await db.commit()


async def cache_list_videos(limit: int = 50) -> list[dict]:
    """Return cached videos ordered by most-recently updated."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT video_id, url, title, channel, duration_sec, thumbnail_url, "
        "created_at, updated_at FROM video_cache ORDER BY updated_at DESC LIMIT ?",
        (limit,),
    )
    return [dict(r) for r in await cursor.fetchall()]


async def cache_delete_video(video_id: str) -> None:
    """Delete a cached video and cascade-delete its clips."""
    db = await get_db()
    await db.execute("DELETE FROM video_cache WHERE video_id = ?", (video_id,))
    await db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# CLIP CANDIDATES CRUD
# ═══════════════════════════════════════════════════════════════════════════════


async def clips_save_candidates(video_id: str, candidates: list[dict]) -> None:
    """Replace all clip candidates for a video with a new ranked set."""
    db = await get_db()
    await db.execute("DELETE FROM clip_candidates WHERE video_id = ?", (video_id,))

    for idx, c in enumerate(candidates):
        virality = c.get("virality", {})
        upload_kit = c.get("upload_kit", {})

        await db.execute(
            """INSERT INTO clip_candidates (
                video_id, clip_id, rank, title_hook, start_sec, end_sec,
                virality_score,
                score_visual_hook, score_replay_loop,
                score_debate_bait, score_payoff_speed,
                banner_text_a, banner_text_b,
                needs_easter_egg_zoom, easter_egg_description,
                upload_kit_json, gemini_raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                video_id,
                c.get("clip_id", f"clip_{idx + 1}"),
                c.get("rank", idx + 1),
                c.get("title_hook", ""),
                c.get("start_sec", 0),
                c.get("end_sec", 0),
                (
                    virality.get("three_second_visual_hook", 0) * 0.30
                    + virality.get("replay_loop_factor", 0) * 0.25
                    + virality.get("debate_comment_bait_potential", 0) * 0.25
                    + virality.get("payoff_speed", 0) * 0.20
                )
                if virality
                else c.get("virality_score", 0),
                virality.get("three_second_visual_hook", c.get("score_visual_hook", 0)),
                virality.get("replay_loop_factor", c.get("score_replay_loop", 0)),
                virality.get("debate_comment_bait_potential", c.get("score_debate_bait", 0)),
                virality.get("payoff_speed", c.get("score_payoff_speed", 0)),
                c.get("top_banner_text_a", c.get("banner_text_a", "")),
                c.get("top_banner_text_b", c.get("banner_text_b", "")),
                1 if c.get("needs_easter_egg_zoom", False) else 0,
                c.get("easter_egg_description", ""),
                json.dumps(upload_kit) if isinstance(upload_kit, dict) else str(upload_kit),
                json.dumps(c) if isinstance(c, dict) else "{}",
            ),
        )
    await db.commit()


async def clips_get_by_video(video_id: str) -> list[dict]:
    """Get all clip candidates for a video, ordered by rank."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM clip_candidates WHERE video_id = ? ORDER BY rank ASC",
        (video_id,),
    )
    return [dict(r) for r in await cursor.fetchall()]


async def clips_update_status(
    clip_db_id: int,
    status: str,
    output_a: str = "",
    output_b: str = "",
    cover: str = "",
) -> None:
    """Update a clip's render status and output file paths."""
    db = await get_db()
    await db.execute(
        "UPDATE clip_candidates SET status=?, output_path_a=?, output_path_b=?, cover_path=? WHERE id=?",
        (status, output_a, output_b, cover, clip_db_id),
    )
    await db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# RETENTION VAULT CRUD
# ═══════════════════════════════════════════════════════════════════════════════


async def vault_log_performance(data: dict) -> int:
    """Log post-upload performance metrics. Returns the new row ID."""
    db = await get_db()
    cursor = await db.execute(
        """INSERT INTO retention_vault (
            clip_id, video_id, title_hook, views_48h, avd_pct,
            viewed_pct, swiped_pct, hook_formula, clip_pattern,
            banner_text, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data.get("clip_id", ""),
            data.get("video_id", ""),
            data.get("title_hook", ""),
            data.get("views_48h", 0),
            data.get("avd_pct", 0),
            data.get("viewed_pct", 0),
            data.get("swiped_pct", 0),
            data.get("hook_formula", ""),
            data.get("clip_pattern", ""),
            data.get("banner_text", ""),
            data.get("notes", ""),
        ),
    )
    await db.commit()
    return cursor.lastrowid  # type: ignore[return-value]


async def vault_get_top_winners(limit: int = 5) -> list[dict]:
    """
    Top performers by AVD% — injected into future Viral Brain prompts
    for self-learning hook formula refinement.
    """
    db = await get_db()
    cursor = await db.execute(
        "SELECT clip_id, title_hook, avd_pct, views_48h, hook_formula, "
        "clip_pattern, banner_text "
        "FROM retention_vault WHERE avd_pct > 0 ORDER BY avd_pct DESC LIMIT ?",
        (limit,),
    )
    return [dict(r) for r in await cursor.fetchall()]


async def vault_list_all(limit: int = 100) -> list[dict]:
    """List all retention vault entries, newest first."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM retention_vault ORDER BY logged_at DESC LIMIT ?",
        (limit,),
    )
    return [dict(r) for r in await cursor.fetchall()]


async def vault_update_entry(entry_id: int, data: dict) -> None:
    """Partial update of a retention vault entry."""
    db = await get_db()
    allowed = [
        "views_48h", "avd_pct", "viewed_pct", "swiped_pct",
        "hook_formula", "clip_pattern", "notes",
    ]
    fields: list[str] = []
    values: list[object] = []
    for key in allowed:
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if not fields:
        return
    values.append(entry_id)
    sql = f"UPDATE retention_vault SET {', '.join(fields)} WHERE id = ?"
    await db.execute(sql, values)
    await db.commit()


async def vault_delete_entry(entry_id: int) -> None:
    """Delete a retention vault row."""
    db = await get_db()
    await db.execute("DELETE FROM retention_vault WHERE id = ?", (entry_id,))
    await db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# JOB QUEUE CRUD
# ═══════════════════════════════════════════════════════════════════════════════


async def job_enqueue(
    url: str,
    video_id: str = "",
    settings_json: str = "{}",
    priority: int = 0,
) -> int:
    """Add a video URL to the batch processing queue. Returns the job ID."""
    db = await get_db()
    cursor = await db.execute(
        "INSERT INTO job_queue (video_url, video_id, settings_json, priority) VALUES (?, ?, ?, ?)",
        (url, video_id, settings_json, priority),
    )
    await db.commit()
    return cursor.lastrowid  # type: ignore[return-value]


async def job_get_next_pending() -> Optional[dict]:
    """Dequeue the highest-priority oldest queued job."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM job_queue WHERE status = 'queued' "
        "ORDER BY priority DESC, created_at ASC LIMIT 1"
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


async def job_update_status(
    job_id: int,
    status: str,
    stage: str = "",
    progress: float = 0,
    error: str = "",
) -> None:
    """Update a job's processing status and progress fields."""
    db = await get_db()

    extra_sql = ""
    if status == "processing" and not stage:
        extra_sql = ", started_at = datetime('now')"
    elif status in ("completed", "failed"):
        extra_sql = ", completed_at = datetime('now')"

    await db.execute(
        f"UPDATE job_queue SET status=?, current_stage=?, progress_pct=?, "
        f"error_message=?{extra_sql} WHERE id=?",
        (status, stage, progress, error, job_id),
    )
    await db.commit()


async def job_list_all(limit: int = 50) -> list[dict]:
    """List all jobs, newest first."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM job_queue ORDER BY created_at DESC LIMIT ?", (limit,)
    )
    return [dict(r) for r in await cursor.fetchall()]


async def job_delete(job_id: int) -> None:
    """Remove a job from the queue."""
    db = await get_db()
    await db.execute("DELETE FROM job_queue WHERE id = ?", (job_id,))
    await db.commit()
