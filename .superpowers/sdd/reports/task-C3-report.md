# Task C3 Report: Family AI Config GET/PUT Endpoints

## Status: DONE

## Commits
- `890bae3` feat(backend): family AI config GET/PUT with encrypted key

## Files Changed
- **Created**: `backend/app/repositories/ai_config.py` — `get_or_create(db, family_id)` using SQLAlchemy select
- **Modified**: `backend/app/schemas/ai_config.py` — added `AIConfigRead` (exposes `has_api_key: bool`, never the key) and `AIConfigUpdate`
- **Modified**: `backend/app/routers/ai_config.py` — added GET/PUT routes; C2 catalog/recommend routes untouched
- **Created**: `backend/tests/test_ai_config_crud.py` — 4 TDD tests written and watched fail before implementation

## Test Summary
- Targeted: 4/4 passed (`test_ai_config_crud.py`)
- Full suite: 46/46 passed, 3 warnings (httpx deprecation only)

## Security Self-Review
- `AIConfigRead` has `has_api_key: bool` only; `api_key` and `api_key_encrypted` fields are absent from the schema
- Encryption uses `crypto.encrypt(api_key, get_settings().ai_config_key)` (Fernet)
- If `AI_CONFIG_KEY` is not set, PUT returns HTTP 400 instead of storing plaintext
- Clearing the key is supported: `api_key=""` sets `api_key_encrypted = None`

## Concerns
- None. The `HTTP_422_UNPROCESSABLE_ENTITY` deprecation warning is a FastAPI/httpx version issue pre-existing in the project (also in C2 tests).

## TDD Compliance
- Tests written first, watched all 4 fail with correct reasons (404 + KeyError)
- Minimal production code written to make them pass
- No production code existed before the tests
