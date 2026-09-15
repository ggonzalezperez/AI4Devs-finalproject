# Task UX4: Cabecera del mundo del niño (nombre + islas + inicio) + legibilidad de la lección

Frontend `frontend/`. Rama `feature-ux-improvements`. SIN push.

**Files:**
- Modify: `frontend/src/api/nucleo.ts` (tipo `ChildProfile` + `getProfile`)
- Create: `frontend/src/components/ChildHeader.tsx`
- Modify: `frontend/src/screens/Spark.tsx`, `frontend/src/screens/LessonScreen.tsx`, `frontend/src/screens/MyKnowledge.tsx` (usar ChildHeader; mejorar legibilidad de la lección)
- Modify: `frontend/src/i18n/translations.ts` (claves `child.*`)
- Test: `frontend/src/components/ChildHeader.test.tsx`

## Step 1: `frontend/src/api/nucleo.ts` — añadir
```ts
export type ChildProfile = { name: string; age: number; islands: number };

export function getProfile() {
  return apiFetch<ChildProfile>("/me/profile", { auth: "child" });
}
```

## Step 2: Claves i18n (es y en)
es:
```
    "child.hi": "¡Hola,",
    "child.home": "Inicio",
    "child.islands": "islas",
```
en:
```
    "child.hi": "Hi,",
    "child.home": "Home",
    "child.islands": "islands",
```

## Step 3: Crear `frontend/src/components/ChildHeader.tsx`
```tsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getProfile, type ChildProfile } from "../api/nucleo";
import { useI18n } from "../i18n/I18nContext";

export default function ChildHeader() {
  const [p, setP] = useState<ChildProfile | null>(null);
  const { t } = useI18n();

  useEffect(() => {
    getProfile()
      .then(setP)
      .catch(() => undefined);
  }, []);

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, marginBottom: 6 }}>
      <Link to="/jugar" aria-label={t("child.home")} style={{ fontSize: 22, textDecoration: "none" }}>
        🏠
      </Link>
      {p?.name && (
        <div style={{ fontFamily: "var(--font-head)", fontWeight: 600, color: "var(--teal-dark)" }}>
          {t("child.hi")} {p.name}
        </div>
      )}
      <Link
        to="/jugar/mis-islas"
        style={{ background: "#fff", borderRadius: 999, padding: "4px 12px", fontWeight: 800, color: "var(--coral)", textDecoration: "none", fontSize: 14 }}
      >
        🏝️ {p?.islands ?? 0}
      </Link>
    </div>
  );
}
```

## Step 4: Usar ChildHeader y mejorar legibilidad
Lee cada pantalla y aplica:
- **Spark.tsx**: añade `<ChildHeader />` como **primer hijo** dentro de `<ScreenCard>` (importa `import ChildHeader from "../components/ChildHeader";`).
- **MyKnowledge.tsx**: igual, `<ChildHeader />` como primer hijo del `<ScreenCard>`.
- **LessonScreen.tsx**:
  - importa ChildHeader.
  - En la **vista de lección** (cuando `!playing`), añade `<ChildHeader />` como primer hijo del `<ScreenCard>`.
  - **Legibilidad del cuerpo**: envuelve el párrafo del cuerpo (`<p ...>{lesson.body}</p>`) en una tarjeta blanca legible:
    ```tsx
          <div style={{ background: "#fff", borderRadius: 16, padding: 16, lineHeight: 1.6, fontSize: 16, color: "var(--teal-dark)" }}>
            {lesson.body}
          </div>
    ```
    (sustituye el `<p>` del cuerpo por este `<div>`; conserva título, materia, dato curioso y botón).
No cambies la lógica ni los textos que comprueban los tests existentes (título, "¡A jugar!", opciones del quiz, feedback).

## Step 5: Test `frontend/src/components/ChildHeader.test.tsx`
```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setChildToken } from "../api/client";
import ChildHeader from "./ChildHeader";

beforeEach(() => {
  localStorage.clear();
  setChildToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

test("shows child name and islands", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify({ name: "Nora", age: 7, islands: 3 }), { status: 200 })),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <ChildHeader />
      </MemoryRouter>
    </I18nProvider>,
  );
  expect(await screen.findByText(/Nora/)).toBeInTheDocument();
  expect(screen.getByText(/🏝️ 3/)).toBeInTheDocument();
});
```

## Step 6: Tests + suite + lint
`npm test` → todo PASS (las pantallas existentes deben seguir verdes: ChildHeader hace un fetch a /me/profile que en sus mocks devuelve datos no-perfil, pero está protegido con `p?.name`, así que no rompe). `npm run lint` → limpio.

## Step 7: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): child-world header (name + islands + home) and clearer lesson body"
```
