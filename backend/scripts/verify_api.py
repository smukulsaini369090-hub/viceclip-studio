"""
VICECLIP STUDIO — Automated API Verification Suite
===================================================
Tests all backend API routes directly using httpx ASGI client
to verify schemas, status codes, and responses.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import httpx
from app.main import app

PASS = "✔ PASS"
FAIL = "✘ FAIL"

async def run_suite():
    print("=" * 64)
    print("  VICECLIP STUDIO — BACKEND API END-TO-END VERIFICATION")
    print("=" * 64)

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Healthcheck
        r = await client.get("/api/health")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        assert data.get("status") == "healthy"
        print(f"{PASS}: GET /api/health -> {data}")

        # 2. System Status & Hardware
        r = await client.get("/api/status")
        assert r.status_code == 200
        status_data = r.json()
        assert status_data.get("ffmpeg_available") is True
        assert status_data.get("nvenc_available") is True
        assert status_data.get("encoder") == "h264_nvenc"
        print(f"{PASS}: GET /api/status -> Encoder: {status_data['encoder']}, GPU: {status_data['cuda_device']}, VRAM: {status_data['vram_total_mb']} MB")

        # 3. Settings
        r = await client.get("/api/settings")
        assert r.status_code == 200
        settings_data = r.json()
        assert settings_data.get("gemini_api_key_set") is True
        print(f"{PASS}: GET /api/settings -> Fast: {settings_data['gemini_fast_model']}, Deep: {settings_data['gemini_deep_model']}")

        # 4. Gemini Connection Test
        r = await client.get("/api/gemini/test")
        assert r.status_code == 200
        gemini_test = r.json()
        assert gemini_test.get("success") is True
        print(f"{PASS}: GET /api/gemini/test -> Success: {gemini_test['success']}, Tested: {gemini_test['model_name']}, Models: {len(gemini_test.get('available_models', []))}")

        # 5. Smart Cache List
        r = await client.get("/api/cache")
        assert r.status_code == 200
        cache_list = r.json()
        assert cache_list.get("success") is True
        print(f"{PASS}: GET /api/cache -> Cached videos: {cache_list.get('count', 0)}")

        # 6. Smart Cache Retrieve Video
        r = await client.get("/api/cache/NBV_oeNEaxw")
        assert r.status_code == 200
        cache_video = r.json()
        assert cache_video.get("success") is True
        assert len(cache_video.get("clips", [])) > 0
        print(f"{PASS}: GET /api/cache/NBV_oeNEaxw -> Title: '{cache_video['video']['title'][:35]}...', Clips: {len(cache_video['clips'])}")

        # 7. Analyze Video (Instant Cache hit test)
        r = await client.post("/api/analyze", json={
            "url": "https://youtu.be/NBV_oeNEaxw",
            "settings": {"manual_gemini_mode": False}
        })
        assert r.status_code == 200
        analyze_res = r.json()
        assert analyze_res.get("success") is True
        assert analyze_res.get("cached") is True
        assert len(analyze_res.get("clips", [])) > 0
        print(f"{PASS}: POST /api/analyze -> Cached instant reload: {analyze_res['cached']}, Clips: {len(analyze_res['clips'])}")

        # 8. Manual Gemini Parser
        raw_pasted = """
```json
{
  "analysis_summary": "GTA 6 controversy breakdown",
  "video_type": "review",
  "clips": [
    {
      "clip_id": "clip_manual_1",
      "title_hook": "Is GTA 6 Actually Unplayable?",
      "start_sec": 5.0,
      "end_sec": 35.0,
      "virality": {
        "three_second_visual_hook": 95,
        "replay_loop_factor": 90,
        "debate_comment_bait_potential": 92,
        "payoff_speed": 88
      },
      "top_banner_text_a": "GTA 6 UNPLAYABLE?!",
      "top_banner_text_b": "WORST LAUNCH EVER?",
      "needs_easter_egg_zoom": false,
      "easter_egg_description": "",
      "upload_kit": {
        "titles": ["GTA 6 Unplayable", "GTA 6 Review", "Shocking GTA 6 Launch"],
        "hashtags": ["#GTA6", "#Gaming"],
        "pinned_comment": "Do you agree with the reviews?",
        "best_cover_timestamp_sec": 12.0
      }
    }
  ]
}
```
"""
        r = await client.post("/api/manual-gemini/parse?video_id=NBV_oeNEaxw", json={"json_text": raw_pasted})
        assert r.status_code == 200
        parsed_res = r.json()
        assert parsed_res.get("success") is True
        print(f"{PASS}: POST /api/manual-gemini/parse -> Sanitised Markdown & parsed {len(parsed_res['clips'])} clips")

        # 9. Batch Watchlist Queue
        r = await client.post("/api/batch/add", json={
            "urls": ["https://www.youtube.com/watch?v=NBV_oeNEaxw"],
            "settings": {}
        })
        assert r.status_code == 200
        batch_add = r.json()
        assert batch_add.get("success") is True
        r = await client.get("/api/batch")
        assert r.status_code == 200
        batch_list = r.json()
        print(f"{PASS}: POST /api/batch/add & GET /api/batch -> Enqueued {batch_add.get('queued_count')} items, Queue total: {batch_list.get('total')}")

        # 10. Retention Vault
        r = await client.post("/api/retention-vault", json={
            "clip_id": "clip_1",
            "video_id": "NBV_oeNEaxw",
            "title_hook": "GTA 6 IS A FULL REVOLT?!",
            "views_48h": 45000,
            "avd_pct": 82.5,
            "viewed_pct": 78.0,
            "swiped_pct": 22.0,
            "hook_formula": "Polarizing Question + Fast B-roll",
            "clip_pattern": "Controversy Breakdown",
            "banner_text": "GTA 6 IS A FULL CHUD REVOLT?!",
            "notes": "Strong retention in first 10 seconds."
        })
        assert r.status_code == 200
        vault_add = r.json()
        assert vault_add.get("success") is True
        r = await client.get("/api/retention-vault?limit=5")
        assert r.status_code == 200
        vault_list = r.json()
        print(f"{PASS}: POST /api/retention-vault & GET /api/retention-vault -> Vault entries: {len(vault_list.get('entries', []))}")

        # 11. Render Single Clip
        target_clip_id = parsed_res["clips"][0]["clip_id"]
        r = await client.post("/api/render/clip", json={
            "video_id": "NBV_oeNEaxw",
            "clip_id": target_clip_id,
            "settings": {
                "enable_demucs": False,
                "enable_commentary": False,
                "enable_easter_egg_zoom": False,
                "enable_dead_air_cut": False,
                "enable_dual_hook": True,
                "caption_theme": "vice_city_neon"
            }
        })
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        render_res = r.json()
        assert render_res.get("success") is True
        assert Path(render_res["variant_a_path"]).is_file()
        print(f"{PASS}: POST /api/render/clip -> Rendered: {Path(render_res['variant_a_path']).name} (Encoder: {render_res['encoder_used']})")

    print("=" * 64)
    print("  ✔ ALL 11 API ROUTES PASSED VERIFICATION WITH ZERO ERRORS!")
    print("=" * 64)

if __name__ == "__main__":
    asyncio.run(run_suite())
