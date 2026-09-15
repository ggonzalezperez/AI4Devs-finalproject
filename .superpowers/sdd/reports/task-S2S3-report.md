# Task S2+S3 Report: Story Endpoints

**Status:** DONE

**Commit:** `643898d` — feat(backend): story endpoints (child create/read approved, family list/review)

**Test summary:** 65 passed (6 new in test_story_api.py + 59 pre-existing), 0 failed. Ruff clean.

## Files created/modified
- `backend/app/schemas/story.py` — `StoryRead`, `StoryReview` Pydantic schemas
- `backend/app/routers/stories.py` — Child routes (`/me/stories`) and family routes (`/family/stories`)
- `backend/app/services/story_service.py` — Added `review_story`; updated import to include `_utcnow` from `app.models.story`
- `backend/app/main.py` — Registered `stories.router`
- `backend/tests/test_story_api.py` — 6 tests covering all business rules

## Self-review
- **Auth guards:** Child token rejected on `/family/*` (401); family token rejected on `/me/*` (401); no token returns 401. Verified by `test_auth_guards`.
- **Cross-family isolation:** `get_for_family` filters by `family_id`, so another family's story returns 404 on PUT. Verified by `test_family_cannot_review_other_familys_story`.
- **Child sees only approved:** `list_for_child` called with `status="approved"`; detail endpoint explicitly checks `story.status != "approved"` and raises 404 for pending/rejected. Verified by `test_child_only_sees_approved` and `test_family_rejects_story`.
- **No naming collision:** query param named `status_filter` (not `status`) to avoid shadowing `fastapi.status`.

## Concerns
None. All tests green; no ruff violations; no push performed.
