# Task B2b Report — Chat-style Lesson Screen (Frontend)

**Status:** DONE
**Branch:** feature-lecciones-ricas
**Commit:** 62111b7 — feat(frontend): chat-style lesson conversation (thread + ask + optional per-turn quiz)

## What was done

1. **`frontend/src/api/nucleo.ts`** — Added `getThread(lessonId)` (GET /lessons/{id}/thread → Lesson[]) and `askInLesson(lessonId, curiosity)` (POST /lessons/{id}/ask → Lesson). Kept all existing exports intact.

2. **`frontend/src/i18n/translations.ts`** — Added `"lesson.quizCta"` to both `es` ("🎯 ¿Jugamos un reto?") and `en` ("🎯 Play a challenge?").

3. **`frontend/src/screens/LessonScreen.tsx`** — Full rewrite as chat. `ChatTurn` sub-component renders each turn as child bubble (curiosity) + Chispa bubble (subject, title, body, fun_fact, optional quiz CTA). Main `LessonScreen` loads the thread via `getThread`, renders all turns, shows follow-up chips and free-text form anchored to the last turn. `askInLesson` appends new turns in-place without navigation. The quiz is per-turn and optional (opens inline, result stays in the conversation). `scrollIntoView` is guarded with a typeof function check for jsdom compatibility.

4. **`frontend/src/screens/LessonScreen.test.tsx`** — Rewritten per brief: stubs fetch to return an array with one turn, asserts title ("La lluvia"), body text, and follow-up chip ("¿Y la nieve?") are present.

## Test Results
- **20 test files, 33 tests — all PASS**
- `npm run lint` (tsc --noEmit) — clean

## Notes
- The brief's ChatTurn code didn't render `turn.title`, but the brief's own test asserts `findByText("La lluvia")` (the title). Added a title `<div>` in ChatTurn to satisfy both the spec and the test.
- jsdom has `scrollIntoView` as `undefined` (not missing), so `?.` alone is not sufficient; used `typeof === "function"` guard instead.
