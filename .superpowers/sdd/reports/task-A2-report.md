# Task A2 Report: LessonGenerator Interface + Moderation Stub

## Status
DONE

## Commit
- SHA: `53cf8ac`
- Subject: `feat(backend): LessonGenerator interface + deterministic stub + moderation stub`
- Branch: `feature-entrega3-nucleo` (not pushed)

## Files Created
- `backend/app/services/lesson_generator.py` — `GeneratedLesson` dataclass, `LessonGenerator` Protocol, `StubLessonGenerator` (deterministic, no external deps)
- `backend/app/services/moderation.py` — `ModerationError`, `_BLOCKLIST`, `check_curiosity()`
- `backend/tests/test_lesson_generator.py` — 2 tests (determinism/shape, forced subject)
- `backend/tests/test_moderation.py` — 2 tests (allow clean input, block blocklist term)

## Test Summary
Full suite: **26 passed, 0 failed, 1 warning** (was 22 before A2; +4 new tests, all green).

## TDD Process
1. Wrote both test files → confirmed `ModuleNotFoundError` (red).
2. Implemented `lesson_generator.py` and `moderation.py` verbatim from brief.
3. Re-ran tests → 4/4 pass (green).
4. Full suite → 26/26 pass.

## Notes / Concerns
- No new dependencies added.
- `StubLessonGenerator` is a pure seam: deterministic, O(1), locale-safe, no I/O.
- Blocklist is minimal placeholder; real moderation adapter will replace `check_curiosity` behind the same signature.
- `LessonGenerator` is a `typing.Protocol`, so the stub satisfies it structurally without inheritance.
