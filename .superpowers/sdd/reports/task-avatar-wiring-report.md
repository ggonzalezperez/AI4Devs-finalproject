# Report: task-avatar-wiring — Child Avatar Wiring

**Status:** DONE

**Commit:** `564c8f3` — `feat(frontend): designed child avatars (picker + crew + access + header)`

## What was done

- `frontend/src/api/children.ts`: Added `avatar: string` to `Child` type; `createChild` now accepts and sends `avatar`.
- `frontend/src/api/nucleo.ts`: Added `avatar: string` to `ChildProfile`.
- `frontend/src/i18n/translations.ts`: Added `addExplorer.avatar` key in both `es` ("Elige un avatar") and `en` ("Choose an avatar").
- `frontend/src/screens/AddExplorer.tsx`: Imports Avatar set; adds `avatar` state (default `fox`); renders 9-button radiogroup picker; passes `avatar` to `createChild`.
- `frontend/src/screens/WhoExplores.tsx`: Removed `avatarFor` import; renders `<Avatar id={c.avatar} size={46} />`; passes `avatar` in navigation state.
- `frontend/src/screens/ChildAccess.tsx`: Removed `avatarFor` import; reads `avatar` from `location.state`; renders `<Avatar id={avatar} size={72} />` (falls back to fox if no state).
- `frontend/src/components/ChildHeader.tsx`: Imports `Avatar`; renders it next to child name.
- `backend/app/schemas/knowledge.py`: Added `avatar: str` to `ChildProfile`.
- `backend/app/routers/me.py`: `/me/profile` now returns `avatar=child.avatar`.
- `frontend/src/lib/avatar.ts`: Deleted (no remaining imports).

## Test results

- **Frontend:** 33/33 passed (20 test files); lint clean (tsc --noEmit 0 errors).
- **Backend:** 67/67 passed, 3 deprecation warnings (unrelated to this task).

## Self-review notes

- `Avatar` component falls back to `fox` when `id` is undefined/invalid — ChildAccess test (no navigation state) stays green.
- No remaining `lib/avatar` imports verified with grep.
- i18n key present in both `es` and `en` locales.
- Avatar persists: signup picker → `createChild(avatar)` → API → stored in DB → returned in `/children` → shown in WhoExplores → passed in nav state → shown in ChildAccess; and `/me/profile` now includes `avatar` for ChildHeader.

## Concerns

None. All green, no blocked items.
