"""
VICECLIP STUDIO — FastAPI Server
==================================
The local-first AI viral video clipping studio engineered for GTA 6 YouTube Shorts.
Outperforms OpusClip in clip detection, gaming layout framing, export speed,
and monetization safety.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.analysis import router as analysis_router
from app.api.batch import router as batch_router
from app.api.render import router as render_router
from app.api.system import router as system_router
from app.api.telemetry import router as telemetry_router
from app.api.vault import router as vault_router
from app.config import get_settings
from app.db.database import close_db, get_db
from app.services.batch_worker import start_batch_worker, stop_batch_worker

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("viceclip.server")


# ═══════════════════════════════════════════════════════════════════════════════
# LIFESPAN CONTEXT MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages server startup and graceful shutdown."""
    cfg = get_settings()

    logger.info("=" * 64)
    logger.info("  VICECLIP STUDIO — Booting Backend Server")
    logger.info("  Workspace: %s", cfg.workspace_dir)
    logger.info("=" * 64)

    # 1. Capability & Hardware Check
    caps = cfg.check_capabilities()
    logger.info(
        "Hardware: NVENC=%s, CUDA=%s, Device=%s, Encoder=%s",
        caps["nvenc"], caps["cuda"], caps["cuda_device"], caps["encoder"]
    )

    # 2. Initialize Database & Tables
    await get_db()

    # 3. Start Unattended Batch Watchlist Worker
    start_batch_worker()

    yield

    # Shutdown
    logger.info("Shutting down VICECLIP STUDIO services...")
    await stop_batch_worker()
    await close_db()
    logger.info("Shutdown complete.")


# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="VICECLIP STUDIO",
    version="1.0.0",
    description="Local-first AI viral video clipping studio engineered for GTA 6 YouTube Shorts",
    lifespan=lifespan,
)

# CORS: Allow local Next.js frontend, local networks, and Vercel deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(telemetry_router)
app.include_router(analysis_router)
app.include_router(render_router)
app.include_router(vault_router)
app.include_router(batch_router)
app.include_router(system_router)

# Mount Static Directories for Video Streaming in Frontend
cfg = get_settings()
output_path = Path(cfg.output_dir).resolve()
cache_path = Path(cfg.cache_dir).resolve()

output_path.mkdir(parents=True, exist_ok=True)
cache_path.mkdir(parents=True, exist_ok=True)

app.mount("/output", StaticFiles(directory=str(output_path)), name="output")
app.mount("/cache", StaticFiles(directory=str(cache_path)), name="cache")


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTHCHECK ROOT
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/health", tags=["System & Settings"])
async def health_check() -> dict:
    """Returns basic healthcheck status."""
    return {
        "status": "healthy",
        "app": "VICECLIP STUDIO",
        "version": "1.0.0",
    }
