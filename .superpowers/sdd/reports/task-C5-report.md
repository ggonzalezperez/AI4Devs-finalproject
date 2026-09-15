# Task C5 Report: Wire Lesson Generation to Family AI Config with Safe Fallback

## Status: DONE

## Commit
- SHA: `3068cb7`
- Subject: `feat(backend): wire lesson generation to family AI config with safe fallback`
- Branch: `feature-entrega4-ai-config` (not pushed)

## Changes Made

### Modified: `backend/app/services/lesson_service.py`
- Removed module-level `_generator: LessonGenerator = StubLessonGenerator()` and unused `LessonGenerator` import.
- Added imports: `ai_config as ai_config_repo`, `build_generator` from `app.services.ai_providers`.
- New module-level `_stub = StubLessonGenerator()` for the fallback.
- `create_lesson` now:
  1. Calls `ai_config_repo.get_or_create(db, child.family_id)` to get/create the family's AI config.
  2. Calls `build_generator(cfg)` to get the configured generator.
  3. Tries `generator.generate(...)` — catches ANY exception and falls back to `_stub.generate(...)`.
  4. Best-effort increments `cfg.used_count` (with rollback on failure, so lesson creation is not blocked).
  5. Creates and persists the `Lesson` via `lesson_repo.create`.
- `answer_lesson` and `to_read_dict` left unchanged.

### Created: `backend/tests/test_lesson_provider_wiring.py`
- 3 tests covering: default stub path, provider failure fallback, and provider success with custom generator.
- Uses `monkeypatch.setattr(lesson_service, "build_generator", ...)` as required.

## Test Summary
- Targeted: `3/3 passed` (`test_lesson_provider_wiring.py`)
- Full suite: `55/55 passed` (3.74s)
- Ruff: `All checks passed!`

## Concerns / Notes
- The fallback path is correct: ANY exception from the configured generator silently falls back to the stub, so children never see provider errors.
- The `used_count` increment is best-effort: wrapped in its own try/except with rollback, so a DB hiccup there never blocks lesson delivery.
- `build_generator` is imported directly into the `lesson_service` module namespace (not via fully-qualified path), so monkeypatching works correctly in tests.
- No push made as instructed.
