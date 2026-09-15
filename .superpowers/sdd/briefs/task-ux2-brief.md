# Task UX2: Separar sesión de familia y de niño (el padre no se desloguea)

Frontend `frontend/`. Rama `feature-ux-improvements`. SIN push.
Problema: familia y niño comparten el token `chispa_token`; al entrar el niño con PIN, el padre queda deslogueado. Solución mínima: **dos slots** (`chispa_token` = familia, `chispa_child_token` = niño) y `apiFetch` elige según `auth`.

**Files:**
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/api/nucleo.ts`
- Modify: `frontend/src/screens/ChildAccess.tsx`
- Modify tests: `frontend/src/api/nucleo.test.ts`, `frontend/src/screens/Spark.test.tsx`, `frontend/src/screens/LessonScreen.test.tsx`, `frontend/src/screens/MyKnowledge.test.tsx`, `frontend/src/screens/ChildAccess.test.tsx`

## Step 1: `frontend/src/api/client.ts`
- Añade un segundo slot y getters/setters de niño, y haz que `apiFetch` acepte `auth?: boolean | "child"`.
- Tras `const TOKEN_KEY = "chispa_token";` añade:
```ts
const CHILD_TOKEN_KEY = "chispa_child_token";

export function setChildToken(token: string | null): void {
  if (token) localStorage.setItem(CHILD_TOKEN_KEY, token);
  else localStorage.removeItem(CHILD_TOKEN_KEY);
}

export function getChildToken(): string | null {
  return localStorage.getItem(CHILD_TOKEN_KEY);
}
```
- Cambia el tipo de `Options.auth` a `boolean | "child"` y la resolución del token dentro de `apiFetch`:
```ts
type Options = { method?: string; body?: unknown; auth?: boolean | "child" };
```
y donde antes hacía `if (options.auth) { const token = getToken(); ... }`, ponlo así:
```ts
  if (options.auth) {
    const token = options.auth === "child" ? getChildToken() : getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }
```
(El resto de `apiFetch` igual. `getToken`/`setToken` siguen siendo el slot de **familia**.)

## Step 2: `frontend/src/api/nucleo.ts`
En las 5 funciones (`createLesson`, `getLesson`, `answerLesson`, `getSuggestions`, `getKnowledge`), cambia `auth: true` por `auth: "child"`.

## Step 3: `frontend/src/screens/ChildAccess.tsx`
Importa `setChildToken` (en vez de `setToken`) desde `../api/client` y, donde guarda el token tras el login del niño, usa `setChildToken(res.access_token)` (NO `setToken`, para no pisar la sesión de la familia).

## Step 4: Tests — usar el token de niño
En estos tests, sustituye `setToken("child-tok")` (o el valor que usen) por `setChildToken("child-tok")` e importa `setChildToken` desde `../api/client`:
- `src/api/nucleo.test.ts` (la aserción `Authorization: Bearer child-tok` se mantiene; ahora el token de niño).
- `src/screens/Spark.test.tsx`
- `src/screens/LessonScreen.test.tsx`
- `src/screens/MyKnowledge.test.tsx`

En `src/screens/ChildAccess.test.tsx`, la aserción que comprueba `localStorage.getItem("chispa_token") === "child-tok"` debe pasar a `localStorage.getItem("chispa_child_token") === "child-tok"` (ahora el niño guarda en su slot).

## Step 5: Tests + suite + lint
`npm test` → todo PASS. `npm run lint` → limpio.

## Step 6: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "fix(frontend): separate family and child sessions (parent stays logged in)"
```
