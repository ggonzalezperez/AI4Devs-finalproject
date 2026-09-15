# Task B1a Report: Lecciones ricas backend (teach-based prompt + follow_ups)

**Status:** DONE

**Commit:** `6a5a68b` — `feat(backend): richer age-adapted lessons (teach-based prompt + follow_ups)`

**Branch:** `feature-lecciones-ricas` (NOT pushed)

## Test summary
68 passed, 3 warnings in 4.28s — all green; existing tests unmodified.

## Migration safety
Migration `7eed4f40a009_lesson_follow_ups_column.py` contains ONLY:
- upgrade: `op.add_column('lessons', sa.Column('follow_ups', sa.JSON(), nullable=True))`
- downgrade: `op.drop_column('lessons', 'follow_ups')`
No drops or alters on other tables. Applied successfully.

## Changes made
- `app/services/lesson_generator.py`: Added `field` import; added `follow_ups: list[str] = field(default_factory=list)` to `GeneratedLesson`; enriched stub body/fun_fact/quiz_options and added `follow_ups=[...]` (3 items).
- `app/services/ai_providers.py`: Added `_age_band(age)` helper (3 bands: ≤5, ≤8, 9-12); replaced `_system_prompt` with pedagogy-rich version including follow_ups JSON field; added `follow_ups` parsing in `_parse_lesson` (tolerates missing/non-list → []); bumped `max_tokens` 800→1400 in `ClaudeGenerator`.
- `app/models/lesson.py`: Added `follow_ups: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)`.
- `app/schemas/lesson.py`: Added `follow_ups: list[str] = []` to `LessonRead`.
- `app/services/lesson_service.py`: Added `follow_ups=g.follow_ups` in `Lesson(...)` constructor; added `"follow_ups": lesson.follow_ups or []` in `to_read_dict`.
- `alembic/versions/7eed4f40a009_lesson_follow_ups_column.py`: Non-destructive migration.
- `tests/test_lesson_generator.py`: Added `test_stub_follow_ups_not_empty_and_bounded`.
- `tests/test_lessons_api.py`: Added assertion that response includes `follow_ups` as a list.
- `tests/test_ai_providers.py`: Added `follow_ups` to `_LESSON_JSON`; added assertions on `lesson.follow_ups`.

## Self-review checklist
- follow_ups flows: stub → service → schema → to_read_dict ✓
- parse tolerates missing/non-list follow_ups (→ []) ✓
- existing lessons (NULL) read as [] via `lesson.follow_ups or []` ✓
- Migration is strictly additive (nullable column) ✓
