# Task S4: Frontend — biblioteca y lector de cuentos del niño

Frontend `frontend/`. Rama `feature-cuentos`. SIN push.
El niño ve su biblioteca de cuentos APROBADOS, crea uno nuevo (queda pendiente de aprobación) y abre uno para leerlo.

**Files:**
- Create: `frontend/src/api/stories.ts`
- Create: `frontend/src/screens/StoryLibrary.tsx`
- Create: `frontend/src/screens/StoryReader.tsx`
- Modify: `frontend/src/App.tsx` (rutas)
- Modify: `frontend/src/screens/Spark.tsx` (enlace "Mis cuentos")
- Modify: `frontend/src/i18n/translations.ts` (claves es + en)
- Test: `frontend/src/screens/StoryLibrary.test.tsx`

## Step 1: `frontend/src/api/stories.ts`
```ts
import { apiFetch } from "./client";

export type Story = { id: number; title: string; body: string; status: string };

// --- Niño (auth: "child") ---
export function createStory() {
  return apiFetch<Story>("/me/stories", { method: "POST", auth: "child" });
}

export function getMyStories() {
  return apiFetch<Story[]>("/me/stories", { auth: "child" });
}

export function getMyStory(id: number) {
  return apiFetch<Story>(`/me/stories/${id}`, { auth: "child" });
}

// --- Familia (auth: true) ---
export function getFamilyStories(statusFilter?: string) {
  const q = statusFilter ? `?status_filter=${statusFilter}` : "";
  return apiFetch<Story[]>(`/family/stories${q}`, { auth: true });
}

export function reviewStory(
  id: number,
  action: "approve" | "reject",
  title?: string,
  body?: string,
) {
  const payload: Record<string, unknown> = { action };
  if (title !== undefined) payload.title = title;
  if (body !== undefined) payload.body = body;
  return apiFetch<Story>(`/family/stories/${id}`, { method: "PUT", auth: true, body: payload });
}
```

## Step 2: Claves i18n en `frontend/src/i18n/translations.ts`
Añade estas claves dentro del bloque `es:` (junto a las `islands.*`) y sus equivalentes en el bloque `en:`.
es:
```
    "stories.title": "📚 Mis cuentos",
    "stories.create": "✨ Crear un cuento",
    "stories.creating": "Creando tu cuento...",
    "stories.pending": "¡Listo! Tus padres lo revisarán pronto. 💛",
    "stories.empty": "Aún no tienes cuentos aprobados. ¡Crea el primero!",
    "stories.read": "Leer",
    "stories.back": "← Volver a mis cuentos",
    "stories.notFound": "Cuento no encontrado",
    "spark.myStories": "📚 Mis cuentos",
```
en:
```
    "stories.title": "📚 My stories",
    "stories.create": "✨ Create a story",
    "stories.creating": "Creating your story...",
    "stories.pending": "Done! Your parents will review it soon. 💛",
    "stories.empty": "No approved stories yet. Create your first one!",
    "stories.read": "Read",
    "stories.back": "← Back to my stories",
    "stories.notFound": "Story not found",
    "spark.myStories": "📚 My stories",
```

## Step 3: `frontend/src/screens/StoryLibrary.tsx`
```tsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createStory, getMyStories, type Story } from "../api/stories";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";
import ChildHeader from "../components/ChildHeader";

export default function StoryLibrary() {
  const [stories, setStories] = useState<Story[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [busy, setBusy] = useState(false);
  const [justCreated, setJustCreated] = useState(false);
  const { t } = useI18n();

  function load() {
    getMyStories()
      .then(setStories)
      .catch(() => undefined)
      .finally(() => setLoaded(true));
  }

  useEffect(load, []);

  async function create() {
    setBusy(true);
    setJustCreated(false);
    try {
      await createStory();
      setJustCreated(true);
    } catch {
      // silencioso: el niño no ve errores técnicos
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <ChildHeader />
      <h1>{t("stories.title")}</h1>
      <Button onClick={() => void create()} disabled={busy}>
        {busy ? t("stories.creating") : t("stories.create")}
      </Button>
      {justCreated && (
        <p role="status" style={{ background: "#fff", borderRadius: 16, padding: 12, color: "#0a5a53", fontWeight: 700 }}>
          {t("stories.pending")}
        </p>
      )}
      {loaded && stories.length === 0 && <p style={{ color: "#0a5a53" }}>{t("stories.empty")}</p>}
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {stories.map((s) => (
          <Link
            key={s.id}
            to={`/jugar/cuentos/${s.id}`}
            style={{ background: "#fff", borderRadius: 16, padding: "14px 16px", textDecoration: "none", color: "var(--teal-dark)" }}
          >
            <span style={{ fontSize: 22 }}>📖</span> <strong>{s.title}</strong>
          </Link>
        ))}
      </div>
      <Link to="/jugar" style={{ textAlign: "center", marginTop: 8 }}>
        {t("islands.more")}
      </Link>
    </ScreenCard>
  );
}
```

## Step 4: `frontend/src/screens/StoryReader.tsx`
```tsx
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getMyStory, type Story } from "../api/stories";
import { useI18n } from "../i18n/I18nContext";
import ScreenCard from "../components/ScreenCard";
import ChildHeader from "../components/ChildHeader";

export default function StoryReader() {
  const { id } = useParams();
  const [story, setStory] = useState<Story | null>(null);
  const [loaded, setLoaded] = useState(false);
  const { t } = useI18n();

  useEffect(() => {
    if (!id) return;
    getMyStory(Number(id))
      .then(setStory)
      .catch(() => undefined)
      .finally(() => setLoaded(true));
  }, [id]);

  return (
    <ScreenCard>
      <ChildHeader />
      {story ? (
        <>
          <h1>{story.title}</h1>
          <div style={{ background: "#fff", borderRadius: 16, padding: 16, lineHeight: 1.7, fontSize: 16, color: "var(--teal-dark)" }}>
            {story.body}
          </div>
        </>
      ) : (
        loaded && <p style={{ color: "#0a5a53" }}>{t("stories.notFound")}</p>
      )}
      <Link to="/jugar/cuentos" style={{ textAlign: "center", marginTop: 8 }}>
        {t("stories.back")}
      </Link>
    </ScreenCard>
  );
}
```

## Step 5: Rutas en `frontend/src/App.tsx`
Importa las dos pantallas:
```tsx
import StoryLibrary from "./screens/StoryLibrary";
import StoryReader from "./screens/StoryReader";
```
Y dentro del bloque `<Route element={<ProtectedRoute />}>`, junto a las rutas `/jugar/*`, añade:
```tsx
        <Route path="/jugar/cuentos" element={<StoryLibrary />} />
        <Route path="/jugar/cuentos/:id" element={<StoryReader />} />
```

## Step 6: Enlace en `frontend/src/screens/Spark.tsx`
Lee el archivo. Justo **antes** del cierre `</ScreenCard>` (después del bloque de sugerencias), añade un enlace a la biblioteca:
```tsx
      <Link to="/jugar/cuentos" style={{ textAlign: "center", marginTop: 4 }}>
        {t("spark.myStories")}
      </Link>
```
Añade el import si no está: `import { Link } from "react-router-dom";` (Spark ya importa `useNavigate` de react-router-dom; amplía ese import a `import { Link, useNavigate } from "react-router-dom";`).

## Step 7: Test `frontend/src/screens/StoryLibrary.test.tsx`
```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setChildToken } from "../api/client";
import StoryLibrary from "./StoryLibrary";

beforeEach(() => {
  localStorage.clear();
  setChildToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

test("lists approved stories", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(
        JSON.stringify([{ id: 7, title: "La aventura de Leo", body: "...", status: "approved" }]),
        { status: 200 },
      ),
    ),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <StoryLibrary />
      </MemoryRouter>
    </I18nProvider>,
  );
  expect(await screen.findByText("La aventura de Leo")).toBeInTheDocument();
});
```

## Step 8: Tests + suite + lint
- `npm test` → todo PASS.
- `npm run lint` → limpio.

## Step 9: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): child story library and reader"
```
