# Task C2 Report: AI Model Catalog + Hardware Recommender + Endpoints

## Status
DONE

## Commit
- SHA: `0c95a63`
- Subject: `feat(backend): AI model catalog + hardware recommender + endpoints`
- Branch: `feature-entrega4-ai-config` (no push)

## Files Created/Modified
- `backend/app/services/ai_catalog.py` — OLLAMA_MODELS catalog (6 models), PROVIDERS list (7 providers: stub/ollama/claude enabled; openai/gemini/deepseek/kimi enabled=False), DEFAULT_LOCAL_MODEL, `recommend_local(vram_gb, ram_gb)`
- `backend/app/schemas/ai_config.py` — `HardwareQuery` and `Recommendation` Pydantic models
- `backend/app/routers/ai_config.py` — `GET /family/ai-config/catalog` and `POST /family/ai-config/recommend`, both family-auth protected
- `backend/app/main.py` — added `ai_config` router import and `app.include_router(ai_config.router)`
- `backend/tests/test_ai_catalog.py` — 3 unit tests for `recommend_local`
- `backend/tests/test_ai_config_api.py` — 3 API tests (auth guard, catalog content, recommend endpoint)

## Test Results
- Targeted (6 tests): 6 passed
- Full suite (42 tests): 42 passed, 0 failed
- Only pre-existing deprecation warnings (httpx/starlette, HTTP_422)

## Concerns
None. Implementation is verbatim from the brief. The `recommend_local` tie-breaking (when multiple models share the same max `min_vram_gb`) uses the last one found by `max()` — for the current catalog this is deterministic (deepseek-r1:32b is unique at 24 GB).
