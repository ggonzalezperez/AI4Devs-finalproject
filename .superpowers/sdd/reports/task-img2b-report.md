# Task IMG-2b Report: Image Config Panel + Lesson Image Render (frontend)

## Status: DONE

## Commit
- SHA: d4c642e
- Message: `feat(frontend): image config panel section + lesson image render`
- Branch: `feature-imagenes`

## Tests
40 tests, all pass (22 test files). No failures.

## Changes made

### `frontend/src/api/client.ts`
- Added `assetUrl(path: string): string` helper that prefixes paths with `BASE_URL`.

### `frontend/src/api/aiConfig.ts`
- Added 5 image fields to `AIConfig`: `image_provider`, `image_model`, `image_base_url`, `image_enabled`, `has_image_api_key`.
- Added `image_providers: Provider[]` to `Catalog`.
- Added 5 image fields to `AIConfigUpdate`: `image_provider`, `image_model`, `image_base_url`, `image_api_key`, `image_enabled`.

### `frontend/src/i18n/translations.ts`
- Added `aiPanel.imgTitle`, `aiPanel.imgHelp`, `aiPanel.imgEnable` in both `es` and `en`.

### `frontend/src/screens/AIConfigPanel.tsx`
- Added 6 image state variables: `imageProvider`, `imageModel`, `imageBaseUrl`, `imageApiKey`, `imageEnabled`, `hasImageKey`.
- Extended `useEffect` to populate image state from `getAIConfig()` response.
- Derived `imageProviders`, `currentImg`, `imgModelOptions` from catalog.
- Extended `save()` to include image fields in `putAIConfig` payload and update `hasImageKey` / clear `imageApiKey` on success.
- Added full image config UI block (provider select, model select, base URL input, API key input, enable checkbox) between the text config block and the hardware block.

### `frontend/src/api/nucleo.ts`
- Added `image_url: string | null` to the `Lesson` type.

### `frontend/src/screens/LessonScreen.tsx`
- Imported `assetUrl` from `../api/client`.
- Added `<img>` render inside `ChatTurn` after the title div, conditional on `turn.image_url`.

### `frontend/src/screens/AIConfigPanel.test.tsx`
- Added `image_providers` array to `CATALOG` mock.
- Added image fields to `CONFIG` mock.
- Updated existing test to use `findAllByLabelText("Proveedor")[0]` (since image section adds a second "Proveedor" label).
- Added new test: `"shows image config section"` asserting `/Imágenes en las lecciones/i` is in the document.

### `frontend/src/screens/LessonScreen.test.tsx`
- Added `image_url: null` to `TURN` mock for TypeScript compliance.

## Concerns
None. All tests green, lint clean, no TypeScript errors.
