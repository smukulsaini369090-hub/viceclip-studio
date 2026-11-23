"""
VICECLIP STUDIO — Retention Vault API
=======================================
Endpoints for logging post-upload performance metrics (Views, AVD %,
Viewed vs Swiped %) to train the Self-Learning Viral Brain.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.db.database import (
    vault_delete_entry,
    vault_get_top_winners,
    vault_list_all,
    vault_log_performance,
    vault_update_entry,
)
from app.db.models import RetentionVaultEntry, RetentionVaultUpdate

logger = logging.getLogger("viceclip.api.vault")

router = APIRouter(prefix="/api/retention-vault", tags=["Retention Vault"])


@router.get("")
async def list_vault_entries_endpoint(limit: int = Query(100, ge=1, le=500)) -> dict:
    """Returns all logged post-upload clip performance records."""
    entries = await vault_list_all(limit=limit)
    return {"success": True, "count": len(entries), "entries": entries}


@router.get("/winners")
async def get_top_winners_endpoint(limit: int = Query(5, ge=1, le=20)) -> dict:
    """
    Returns the top-performing clips ranked by Average View Duration (AVD %).
    These hook formulas and patterns are automatically injected into future
    Viral Brain prompts for self-learning optimization.
    """
    winners = await vault_get_top_winners(limit=limit)
    return {"success": True, "count": len(winners), "winners": winners}


@router.post("")
async def log_vault_entry_endpoint(entry: RetentionVaultEntry) -> dict:
    """Logs 48-hour post-upload analytics for a rendered clip."""
    try:
        new_id = await vault_log_performance(entry.model_dump())
        return {
            "success": True,
            "id": new_id,
            "message": "Performance metrics logged into Retention Vault",
        }
    except Exception as exc:
        logger.error("Failed to log retention vault entry: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.patch("/{entry_id}")
async def update_vault_entry_endpoint(entry_id: int, payload: RetentionVaultUpdate) -> dict:
    """Updates views, AVD %, or notes for an existing vault entry."""
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update fields provided")

    await vault_update_entry(entry_id, update_data)
    return {"success": True, "message": f"Vault entry #{entry_id} updated"}


@router.delete("/{entry_id}")
async def delete_vault_entry_endpoint(entry_id: int) -> dict:
    """Removes a record from the Retention Vault."""
    await vault_delete_entry(entry_id)
    return {"success": True, "message": f"Vault entry #{entry_id} deleted"}
