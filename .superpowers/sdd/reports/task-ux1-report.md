# Task UX1 Report — AI Settings Panel UX Improvements

**Status:** DONE

## Commits
- `1150d05` — feat(frontend): clearer AI settings panel (tier info, help text, key note, use-recommended)
  - Branch: `feature-ux-improvements` (no push)

## Changes Made

### `frontend/src/i18n/translations.ts`
Added 9 new `aiPanel.*` keys to both `es` and `en` dictionaries:
`aiPanel.intro`, `aiPanel.tierFree`, `aiPanel.tierByok`, `aiPanel.tierManaged`,
`aiPanel.keyNote`, `aiPanel.useThis`, `aiPanel.localHelp`, `aiPanel.byokHelp`, `aiPanel.freeHelp`.

### `frontend/src/screens/AIConfigPanel.tsx`
Four additions per the brief:
1. **Tier info card** — rendered between the subtitle and the form, showing intro + 3 tier lines.
2. **Provider help text** — a `<p>` placed *after* (not inside) the provider `<label>` showing context-sensitive help (ollama/byok/free).
3. **Key note** — a `<small>` placed *after* (not inside) the API key `<label>` with the encryption notice.
4. **"Usar este modelo" button** — appears below `rec.note` when a recommendation exists; sets provider to `ollama` and model to `rec.recommended`.

## Test Results
- Targeted: `AIConfigPanel.test.tsx` — 1/1 PASS
- Full suite: 26/26 tests, 16 files — all PASS
- Lint (`tsc --noEmit`): clean, no errors

## One Concern (Resolved)
Placing `<p>` inside `<label>` breaks the accessible-name computation in `@testing-library` (label text becomes "Proveedor + help text" instead of "Proveedor"). Moved both the help `<p>` and the key `<small>` outside their respective `<label>` tags — visually identical, semantically correct, and test-compatible.
