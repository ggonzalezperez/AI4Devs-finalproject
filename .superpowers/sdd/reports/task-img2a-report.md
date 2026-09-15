# Task IMG-2a Report — Image Config in AI Panel (backend)

**Status:** DONE

## What was done

### Files modified
- `backend/app/schemas/ai_config.py` — Added image fields to `AIConfigRead` (`image_provider`, `image_model`, `image_base_url`, `image_enabled`, `has_image_api_key`) and `AIConfigUpdate` (`image_provider`, `image_model`, `image_base_url`, `image_api_key`, `image_enabled` with safe defaults).
- `backend/app/routers/ai_config.py` — Updated `_to_read()` to include image fields; updated `put_config` to persist image config with encryption mirroring the text key pattern; added `image_providers` to the catalog endpoint response.
- `backend/tests/test_ai_config_api.py` — Added 4 new tests: defaults check, round-trip PUT/GET with encrypted key, empty-string clear, and catalog `image_providers` presence.

## Test results
`95 passed, 4 warnings` — all existing + new tests green. `ruff check` clean.

## Commit
`17f16ff` — `feat(backend): expose image generation settings in the AI config panel API`

## Self-review checklist
- Image key never returned in plaintext — only `has_image_api_key: bool` exposed.
- Empty string `image_api_key=""` clears the stored key (sets `image_api_key_encrypted = None`).
- Defaults: `image_provider="none"`, `image_enabled=False`, `has_image_api_key=False`.
- Catalog exposes `image_providers` list (5 entries, includes `huggingface`).
- Text (provider/model/api_key) behavior unchanged.
