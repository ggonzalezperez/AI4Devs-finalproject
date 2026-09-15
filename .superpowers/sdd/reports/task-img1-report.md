# Task IMG-1 Report: Backend Image Generation Seam

**Status:** DONE
**Branch:** feature-imagenes
**Commit:** 771ac89 — feat(backend): image generation seam (HF/local-SDXL/OpenAI/Gemini), default off

## Test Summary

88 passed, 0 failed, 4 warnings (pre-existing deprecation warnings from starlette/httpx)
8 new tests in `tests/test_images.py` — all green.

## Migration Safety

Migration `9ba3ea142d38` — only `op.add_column` statements:

```
op.add_column('family_ai_config', sa.Column('image_provider', sa.String(20), nullable=False, server_default='none'))
op.add_column('family_ai_config', sa.Column('image_model', sa.String(120), nullable=True))
op.add_column('family_ai_config', sa.Column('image_base_url', sa.String(255), nullable=True))
op.add_column('family_ai_config', sa.Column('image_api_key_encrypted', sa.String(500), nullable=True))
op.add_column('family_ai_config', sa.Column('image_enabled', sa.Boolean(), nullable=False, server_default=sa.false()))
op.add_column('lessons', sa.Column('image_url', sa.String(500), nullable=True))
```

No drops, no alters on other tables. Non-destructive. `server_default` added manually for the two NOT NULL columns (SQLite requirement).

## Self-Review Checklist

- [x] Default config → `build_image_generator(cfg)` returns `StubImageGenerator` → `generate()` returns None → `_attach_image` returns early → `lesson.image_url` stays None
- [x] Generator exceptions swallowed: test `test_attach_image_swallows_generator_exception` verifies no crash, `image_url` stays None
- [x] Image saved to `media/lessons/{id}.png`: test `test_attach_image_writes_file_and_sets_url` with `tmp_path`
- [x] `lesson.image_url` set to `/media/lessons/{id}.png` after write
- [x] Key decryption in `image_providers.py` uses `crypto.decrypt(encrypted, get_settings().ai_config_key)` — mirrors text path in `ai_providers.py`
- [x] API test confirms `image_url is None` for default family config
- [x] Existing 80 tests remain green

## Files Modified

- `backend/app/config.py` — added `media_dir`, `image_timeout`
- `backend/app/models/ai_config.py` — added 5 image_* columns
- `backend/app/models/lesson.py` — added `image_url`
- `backend/app/main.py` — mount `/media` StaticFiles
- `backend/app/services/lesson_service.py` — `_attach_image`, calls in `create_lesson` + `continue_conversation`, `to_read_dict` updated
- `backend/app/schemas/lesson.py` — `LessonRead.image_url`
- `backend/app/services/ai_catalog.py` — `IMAGE_PROVIDERS`
- `.gitignore` — `media/` + `backend/media/`

## Files Created

- `backend/app/services/image_generator.py`
- `backend/app/services/image_providers.py`
- `backend/tests/test_images.py`
- `backend/alembic/versions/9ba3ea142d38_image_generation_config_lesson_image_url.py`
