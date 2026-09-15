# Task TTS Report — Read-aloud lessons (Web Speech Synthesis)

**Status:** DONE
**Branch:** feature-fasec-extra
**Commit:** 774e38e — feat(frontend): read-aloud lessons (Web Speech Synthesis, multilingual)

## Files changed

- **Created** `frontend/src/components/SpeakButton.tsx` — button that calls `window.speechSynthesis`; returns `null` when API unsupported (jsdom).
- **Created** `frontend/src/components/SpeakButton.test.tsx` — 2 tests: unsupported → no button; supported → aria-labeled button visible.
- **Modified** `frontend/src/screens/LessonScreen.tsx` — imported `SpeakButton`; replaced the plain title `<div>` in `ChatTurn` with a flex row containing the title + `<SpeakButton text={title + body + fun_fact} />`.
- **Modified** `frontend/src/i18n/translations.ts` — added `voice.listen` in both `es` ("Escuchar la lección") and `en` ("Listen to the lesson").

## Self-review checklist

- Unsupported browser → `null` returned before render, no button shown.
- Supported → button toggles 🔊/⏹️, `aria-pressed` reflects state.
- Language mapping: `lang === "en"` → `en-US`, else → `es-ES`.
- Reads `title + body + fun_fact` concatenated.
- `useEffect` cleanup cancels any active speech on unmount.
- Existing `LessonScreen` tests unaffected (jsdom has no `speechSynthesis`).

## Test results

`npm test` — 42 tests / 23 files, all PASS.
`npm run lint` (tsc --noEmit) — clean, no errors.

## Concerns

None. Implementation is verbatim from the brief.
