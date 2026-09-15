# Task Voz Report

**Status:** DONE

**Commit:** `36b4684` — `feat(frontend): voice dictation for questions (Web Speech API, multilingual)`

**Tests:** 38/38 passed (21 test files). `MicButton.test.tsx` adds 2 new tests; all pre-existing Spark and LessonScreen tests remain green (MicButton renders null in jsdom — no impact).

**Lint:** `tsc --noEmit` clean — zero errors.

**`useI18n` exposes `lang`:** YES. The context type is `{ lang: Lang; setLang: (l: Lang) => void; t: (key: string) => string }`, so the primary brief variant was used verbatim (`const { t, lang } = useI18n()`). No `document.documentElement.lang` fallback needed.

## Files changed

- **Created** `frontend/src/components/MicButton.tsx` — typed `RecognitionLike`/`RecognitionCtor` wrappers, `getRecognitionCtor()` helper, graceful null return when unsupported, `lang` → BCP-47 mapping (`en` → `en-US`, anything else → `es-ES`).
- **Created** `frontend/src/components/MicButton.test.tsx` — 2 tests: unsupported (renders nothing) + supported via `vi.stubGlobal("SpeechRecognition", FakeRec)`.
- **Modified** `frontend/src/i18n/translations.ts` — added `"voice.dictate"` key in both `es` and `en` dicts.
- **Modified** `frontend/src/screens/Spark.tsx` — curiosity input wrapped in `<div style={{ display: "flex", gap: 8 }}>` with `<MicButton onText={setCuriosity} disabled={busy} />`.
- **Modified** `frontend/src/screens/LessonScreen.tsx` — `<MicButton onText={setQuestion} disabled={busy} />` inserted between the chat input and the submit button.

## Self-review checklist

- Unsupported browser → `getRecognitionCtor()` returns null → component returns null → no button rendered.
- Supported browser → mic button renders with `aria-label={t("voice.dictate")}` and `aria-pressed` toggle.
- Transcript → `onresult` callback → `onText(transcript)` → sets the controlled input state.
- Language: `lang === "en"` → `"en-US"`, otherwise `"es-ES"`.
- No `any` casts — all `window` widening uses `unknown` intermediary; `RecognitionLike`/`RecognitionCtor` fully typed.
- No new npm dependencies.
- Branch `feature-buscador-voz`, no push.

## Concerns

None. Implementation is minimal, idiomatic, and fully covered by the degradation + stub tests.
