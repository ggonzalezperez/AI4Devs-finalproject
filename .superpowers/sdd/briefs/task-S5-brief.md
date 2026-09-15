# Task S5: Frontend — panel de aprobación de cuentos de la familia

Frontend `frontend/`. Rama `feature-cuentos`. SIN push.
Los padres ven todos los cuentos de sus hijos, pueden editar el título/cuerpo y aprobar o rechazar. Depende de S4 (ya existe `frontend/src/api/stories.ts` con `getFamilyStories` y `reviewStory`).

**Files:**
- Create: `frontend/src/screens/FamilyStories.tsx`
- Modify: `frontend/src/App.tsx` (ruta `/familia/cuentos`)
- Modify: `frontend/src/screens/WhoExplores.tsx` (enlace a revisar cuentos)
- Modify: `frontend/src/i18n/translations.ts` (claves es + en)
- Test: `frontend/src/screens/FamilyStories.test.tsx`

## Step 1: Claves i18n en `frontend/src/i18n/translations.ts`
Añade en el bloque `es:` y sus equivalentes en `en:`.
es:
```
    "familyStories.title": "📚 Cuentos para revisar",
    "familyStories.subtitle": "Aprueba, edita o rechaza los cuentos antes de que tus hijos los lean.",
    "familyStories.empty": "No hay cuentos todavía.",
    "familyStories.pending": "Pendiente",
    "familyStories.approved": "Aprobado",
    "familyStories.rejected": "Rechazado",
    "familyStories.approve": "✅ Aprobar",
    "familyStories.reject": "🚫 Rechazar",
    "familyStories.titleLabel": "Título",
    "familyStories.bodyLabel": "Cuento",
    "familyStories.error": "No se pudieron cargar los cuentos",
    "familyStories.link": "📚 Revisar cuentos",
```
en:
```
    "familyStories.title": "📚 Stories to review",
    "familyStories.subtitle": "Approve, edit or reject stories before your children read them.",
    "familyStories.empty": "No stories yet.",
    "familyStories.pending": "Pending",
    "familyStories.approved": "Approved",
    "familyStories.rejected": "Rejected",
    "familyStories.approve": "✅ Approve",
    "familyStories.reject": "🚫 Reject",
    "familyStories.titleLabel": "Title",
    "familyStories.bodyLabel": "Story",
    "familyStories.error": "Could not load stories",
    "familyStories.link": "📚 Review stories",
```

## Step 2: `frontend/src/screens/FamilyStories.tsx`
Cada cuento pendiente muestra campos editables (título + cuerpo) y botones Aprobar/Rechazar; "Aprobar" envía los valores actuales de los campos. Los aprobados/rechazados se muestran con su estado, sin edición.
```tsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getFamilyStories, reviewStory, type Story } from "../api/stories";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

export default function FamilyStories() {
  const [stories, setStories] = useState<Story[]>([]);
  const [error, setError] = useState("");
  const [loaded, setLoaded] = useState(false);
  const { t } = useI18n();

  function load() {
    getFamilyStories()
      .then(setStories)
      .catch(() => setError(t("familyStories.error")))
      .finally(() => setLoaded(true));
  }

  useEffect(load, []);

  const statusLabel: Record<string, string> = {
    pending: t("familyStories.pending"),
    approved: t("familyStories.approved"),
    rejected: t("familyStories.rejected"),
  };

  return (
    <ScreenCard>
      <div>
        <h1>{t("familyStories.title")}</h1>
        <p style={{ margin: "4px 0 0", color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>
          {t("familyStories.subtitle")}
        </p>
      </div>
      {error && <p role="alert">{error}</p>}
      {loaded && stories.length === 0 && !error && (
        <p style={{ color: "#0a5a53", fontWeight: 600 }}>{t("familyStories.empty")}</p>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {stories.map((s) => (
          <StoryRow key={s.id} story={s} statusLabel={statusLabel} onReviewed={load} />
        ))}
      </div>
      <Link to="/familia/explorar" style={{ textAlign: "center", marginTop: 8 }}>
        ←
      </Link>
    </ScreenCard>
  );
}

function StoryRow({
  story,
  statusLabel,
  onReviewed,
}: {
  story: Story;
  statusLabel: Record<string, string>;
  onReviewed: () => void;
}) {
  const [title, setTitle] = useState(story.title);
  const [body, setBody] = useState(story.body);
  const [busy, setBusy] = useState(false);
  const { t } = useI18n();
  const pending = story.status === "pending";

  async function review(action: "approve" | "reject") {
    setBusy(true);
    try {
      await reviewStory(story.id, action, title, body);
      onReviewed();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ background: "#fff", borderRadius: 16, padding: 16, display: "flex", flexDirection: "column", gap: 8 }}>
      <span style={{ fontSize: 12, fontWeight: 800, color: "var(--coral)" }}>
        {statusLabel[story.status] ?? story.status}
      </span>
      {pending ? (
        <>
          <label style={{ fontSize: 12, fontWeight: 700, color: "#0a5a53" }}>
            {t("familyStories.titleLabel")}
          </label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} aria-label={t("familyStories.titleLabel")} />
          <label style={{ fontSize: 12, fontWeight: 700, color: "#0a5a53" }}>
            {t("familyStories.bodyLabel")}
          </label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            rows={5}
            aria-label={t("familyStories.bodyLabel")}
            style={{ fontFamily: "inherit", fontSize: 14, lineHeight: 1.5 }}
          />
          <div style={{ display: "flex", gap: 8 }}>
            <Button onClick={() => void review("approve")} disabled={busy}>
              {t("familyStories.approve")}
            </Button>
            <button onClick={() => void review("reject")} disabled={busy} style={{ padding: "10px 14px" }}>
              {t("familyStories.reject")}
            </button>
          </div>
        </>
      ) : (
        <>
          <strong style={{ color: "var(--teal-dark)" }}>{story.title}</strong>
          <p style={{ color: "#0a5a53", margin: 0, lineHeight: 1.5 }}>{story.body}</p>
        </>
      )}
    </div>
  );
}
```

## Step 3: Ruta en `frontend/src/App.tsx`
Importa `import FamilyStories from "./screens/FamilyStories";` y, junto a las rutas `/familia/*` dentro de `<ProtectedRoute />`, añade:
```tsx
        <Route path="/familia/cuentos" element={<FamilyStories />} />
```

## Step 4: Enlace en `frontend/src/screens/WhoExplores.tsx`
Lee el archivo. Junto al enlace `<Link to="/familia/ia">` (el de configurar IA), añade un enlace al panel de cuentos:
```tsx
      <Link to="/familia/cuentos" style={{ textAlign: "center", marginTop: 4 }}>
        {t("familyStories.link")}
      </Link>
```

## Step 5: Test `frontend/src/screens/FamilyStories.test.tsx`
```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setToken } from "../api/client";
import FamilyStories from "./FamilyStories";

beforeEach(() => {
  localStorage.clear();
  setToken("fam-tok");
});
afterEach(() => vi.restoreAllMocks());

test("shows a pending story with approve control", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(
        JSON.stringify([{ id: 3, title: "Cuento de Leo", body: "Érase una vez...", status: "pending" }]),
        { status: 200 },
      ),
    ),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <FamilyStories />
      </MemoryRouter>
    </I18nProvider>,
  );
  expect(await screen.findByDisplayValue("Cuento de Leo")).toBeInTheDocument();
  expect(screen.getByText(/Aprobar/)).toBeInTheDocument();
});
```
(Nota: la familia usa `setToken` — slot `chispa_token` — NO `setChildToken`.)

## Step 6: Tests + suite + lint
- `npm test` → todo PASS.
- `npm run lint` → limpio.

## Step 7: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): family story approval panel"
```
