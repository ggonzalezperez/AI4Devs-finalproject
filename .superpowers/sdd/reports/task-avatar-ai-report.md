# Task AVATAR-IA — Implementation Report

## Status
COMPLETE — all tests pass, lint clean, migration safe, committed.

## Commit
- **SHA:** `d521723`
- **Subject:** `feat: AI-generated child avatars (reuses image seam, falls back to curated set)`
- **Branch:** `feature-fasec-extra`
- **Files changed:** 19 (4 new: migration, backend test, frontend test, ChildAvatar screen)

## Backend Test Summary
```
98 passed, 4 warnings in 6.13s
```
3 new tests from `test_avatar_ai.py` all pass:
- `test_build_avatar_prompt_contains_description` — unit test on prompt builder
- `test_generate_avatar_disabled_returns_409` — default stub generator returns 409
- `test_generate_avatar_wrong_family_returns_404` — cross-family isolation

## Frontend Test Summary
```
24 test files, 44 tests — all passed (5.47s)
```
2 new tests from `Avatar.test.tsx` pass:
- `Avatar renders SVG when no imageUrl`
- `Avatar renders img tag when imageUrl provided`

## Migration Safety Note
Migration file: `alembic/versions/7005ca28f0c3_child_avatar_image_url.py`

The only database operation in `upgrade()`:
```python
op.add_column('children', sa.Column('avatar_image_url', sa.String(length=500), nullable=True))
```
No drops, no alters on other tables — safe to apply at any time.

## Changes Summary

### Backend
| File | Change |
|------|--------|
| `app/models/child.py` | Added `avatar_image_url: Mapped[str | None]` column |
| `app/schemas/child.py` | Added `avatar_image_url` to `ChildRead`; new `AvatarGenerate` schema |
| `app/schemas/knowledge.py` | Added `avatar_image_url` to `ChildProfile` |
| `app/routers/me.py` | Pass `avatar_image_url` in `my_profile` return |
| `app/services/image_generator.py` | Added `build_avatar_prompt()` |
| `app/routers/children.py` | Added `POST /{child_id}/avatar/generate` endpoint |
| `tests/test_avatar_ai.py` | New — 3 tests |
| `alembic/versions/7005ca28f0c3_...py` | New migration: add_column only |

### Frontend
| File | Change |
|------|--------|
| `api/children.ts` | Added `avatar_image_url` to `Child` type; `generateChildAvatar()` fn |
| `api/nucleo.ts` | Added `avatar_image_url` to `ChildProfile` type |
| `components/avatars.tsx` | Added `imageUrl` prop; renders `<img>` when provided, SVG fallback |
| `screens/WhoExplores.tsx` | `imageUrl` prop on Avatar; sparkle link to ChildAvatar screen |
| `components/ChildHeader.tsx` | `imageUrl` prop on Avatar |
| `screens/ChildAvatar.tsx` | New screen — input + generate button + avatar preview |
| `App.tsx` | New route `/familia/explorador/:childId` |
| `i18n/translations.ts` | 6 new keys per language (`avatarAI.*`) |
| `screens/WhoExplores.test.tsx` | `avatar_image_url: null` in mock data |
| `components/ChildHeader.test.tsx` | `avatar_image_url: null` in mock data |
| `components/Avatar.test.tsx` | New — 2 tests |

## Concerns
- None. The feature correctly degrades: when image generation is not configured, the endpoint returns HTTP 409 and the curated SVG avatar set is used as fallback.
