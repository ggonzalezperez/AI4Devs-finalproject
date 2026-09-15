# Task B3 Report — Archipelago Search (buscador)

**Status:** DONE
**Commit:** 22d5715 — feat(frontend): archipelago search to find islands already explored
**Branch:** feature-buscador-voz

## Changes

### `frontend/src/i18n/translations.ts`
Added `islands.search` and `islands.noMatch` to both `es` and `en` dictionaries verbatim per the brief.

### `frontend/src/screens/MyKnowledge.tsx`
- Added `const [query, setQuery] = useState("")` search state.
- Added `norm()` helper (NFD decompose + lowercase) and `filtered` derived list.
- Input rendered above the island grid, visible only when `loaded && nodes.length > 0`.
- `nodes.map(...)` replaced with `filtered.map(...)` — island link structure via `root_lesson_id` preserved exactly.
- "No match" paragraph rendered when `loaded && nodes.length > 0 && filtered.length === 0`.
- "No islands" empty-state (`islands.empty`) unchanged.

### `frontend/src/screens/MyKnowledge.test.tsx`
- Added `fireEvent` to import.
- New test: two-island mock (flotabilidad + volcanes), types "volca" in search box, asserts volcanes visible and flotabilidad absent.

## Test results
36/36 tests PASS. `npm run lint` (tsc --noEmit) clean.

## Self-review checklist
- [x] Filters by concept and subject, accent- and case-insensitive
- [x] "No match" message only when there ARE islands but none match
- [x] Empty-state message unchanged (no islands path)
- [x] Islands still link to their conversations via root_lesson_id
- [x] No backend changes
