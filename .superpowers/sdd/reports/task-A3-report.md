# Task A3 Report: Lessons Endpoints (generate + get)

## Status: DONE

## Commit
- SHA: `bfa2800`
- Message: `feat(backend): lessons endpoints (generate + get) with moderation`

## Files Created
- `backend/app/schemas/lesson.py` — LessonCreate, QuizPublic (no correct_index), LessonRead
- `backend/app/repositories/lesson.py` — create / get_for_child (ownership-enforced)
- `backend/app/services/lesson_service.py` — create_lesson (check_curiosity → generate → persist) + to_read_dict
- `backend/app/routers/lessons.py` — POST /lessons (201) + GET /lessons/{id}, ModerationError → 422
- `backend/tests/test_lessons_api.py` — 3 tests per brief (verbatim)

## Files Modified
- `backend/app/main.py` — added `lessons` to import + `app.include_router(lessons.router)`; CORS and existing routers untouched

## Test Summary
- Targeted: 3/3 PASSED (`test_lessons_api.py`)
- Full suite: 29/29 PASSED (no regressions)

## Concerns
- Two Starlette deprecation warnings (unrelated to this task): `HTTP_422_UNPROCESSABLE_ENTITY` → `HTTP_422_UNPROCESSABLE_CONTENT` and `httpx` testclient; existing warnings, not introduced here.
- `quiz_options` stored as JSON in DB returns a Python list; `LessonRead.model_validate(to_read_dict(lesson))` pattern bypasses ORM→Pydantic friction cleanly.

## Branch
`feature-entrega3-nucleo` — no push performed.
