# Task B4: "Mis conocimientos" (archipiélago) + cableado final del mundo del niño

Usa el código EXACTO. Frontend `frontend/`. Rama `feature-entrega3-nucleo`. SIN push.

**Files:**
- Create: `frontend/src/screens/MyKnowledge.tsx`
- Modify: `frontend/src/screens/ChildAccess.tsx` (al acertar PIN → navegar a `/jugar`)
- Modify: `frontend/src/App.tsx` (registrar rutas Spark/LessonScreen/MyKnowledge)
- Modify: `frontend/src/i18n/translations.ts` (claves islands.*)
- Test: `frontend/src/screens/MyKnowledge.test.tsx`

## Step 1: Añadir claves i18n (es y en), sin tocar existentes

es:
```
    "islands.title": "Tu archipiélago 🗺️",
    "islands.empty": "Aún no hay islas. ¡Enciende una chispa!",
    "islands.more": "Descubrir más",
```
en:
```
    "islands.title": "Your archipelago 🗺️",
    "islands.empty": "No islands yet. Light a spark!",
    "islands.more": "Discover more",
```

## Step 2: Test `frontend/src/screens/MyKnowledge.test.tsx`

```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setToken } from "../api/client";
import MyKnowledge from "./MyKnowledge";

beforeEach(() => {
  localStorage.clear();
  setToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

test("lists knowledge islands", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(JSON.stringify([{ id: 1, concept: "flotabilidad", subject: "ciencia", mastery: 2 }]), { status: 200 }),
    ),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <MyKnowledge />
      </MemoryRouter>
    </I18nProvider>,
  );
  expect(await screen.findByText("flotabilidad")).toBeInTheDocument();
});
```

## Step 3: Crear `frontend/src/screens/MyKnowledge.tsx`

```tsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getKnowledge, type KnowledgeNode } from "../api/nucleo";
import { useI18n } from "../i18n/I18nContext";
import ScreenCard from "../components/ScreenCard";

export default function MyKnowledge() {
  const [nodes, setNodes] = useState<KnowledgeNode[]>([]);
  const [loaded, setLoaded] = useState(false);
  const { t } = useI18n();

  useEffect(() => {
    getKnowledge()
      .then(setNodes)
      .catch(() => undefined)
      .finally(() => setLoaded(true));
  }, []);

  return (
    <ScreenCard>
      <h1>{t("islands.title")}</h1>
      {loaded && nodes.length === 0 && <p style={{ color: "#0a5a53" }}>{t("islands.empty")}</p>}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
        {nodes.map((n) => (
          <div key={n.id} style={{ background: "#fff", borderRadius: 16, padding: "12px 14px", minWidth: 120 }}>
            <div style={{ fontSize: 26 }}>🏝️</div>
            <strong>{n.concept}</strong>
            <div style={{ fontSize: 12, color: "#0a5a53" }}>
              {n.subject} · ⭐ {n.mastery}
            </div>
          </div>
        ))}
      </div>
      <Link to="/jugar" style={{ textAlign: "center", marginTop: 8 }}>
        {t("islands.more")}
      </Link>
    </ScreenCard>
  );
}
```

## Step 4: Reemplazar `frontend/src/screens/ChildAccess.tsx` (ahora navega a /jugar al acertar)

```tsx
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { childLogin } from "../api/children";
import { setToken } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import { avatarFor } from "../lib/avatar";
import ScreenCard from "../components/ScreenCard";

export default function ChildAccess() {
  const { childId } = useParams();
  const navigate = useNavigate();
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const { t } = useI18n();

  useEffect(() => {
    if (pin.length === 4 && childId) {
      childLogin(Number(childId), pin)
        .then((res) => {
          setToken(res.access_token);
          navigate("/jugar");
        })
        .catch(() => {
          setError(t("childAccess.error"));
          setPin("");
        });
    }
  }, [pin, childId, t, navigate]);

  const keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "⌫"];

  return (
    <ScreenCard>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: 52 }}>{avatarFor(Number(childId))}</div>
        <div style={{ color: "#0a5a53", fontWeight: 600, marginTop: 2 }}>{t("childAccess.title")}</div>
      </div>
      <div aria-label="pin" style={{ display: "flex", gap: 14, justifyContent: "center", marginTop: 6 }}>
        {[0, 1, 2, 3].map((i) => (
          <span
            key={i}
            style={{
              width: 16,
              height: 16,
              borderRadius: 99,
              background: i < pin.length ? "var(--coral)" : "rgba(255,255,255,.5)",
            }}
          />
        ))}
      </div>
      {error && <p role="alert" style={{ textAlign: "center", color: "#fff", fontWeight: 700 }}>{error}</p>}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 14, marginTop: 14 }}>
        {keys.map((k, idx) =>
          k === "" ? (
            <div key={idx} />
          ) : (
            <button
              key={idx}
              onClick={() =>
                k === "⌫" ? setPin((p) => p.slice(0, -1)) : setPin((p) => (p + k).slice(0, 4))
              }
            >
              {k}
            </button>
          ),
        )}
      </div>
    </ScreenCard>
  );
}
```

Nota: la pantalla de niño existente `ChildAccess.test.tsx` solo comprueba que se guarda el token tras 4 dígitos; este cambio lo mantiene (setToken antes de navigate), así que sigue pasando.

## Step 5: Reemplazar `frontend/src/App.tsx` (añade las 3 rutas del mundo del niño)

```tsx
import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./routes/ProtectedRoute";
import CreateFamily from "./screens/CreateFamily";
import Login from "./screens/Login";
import AddExplorer from "./screens/AddExplorer";
import WhoExplores from "./screens/WhoExplores";
import ChildAccess from "./screens/ChildAccess";
import Spark from "./screens/Spark";
import LessonScreen from "./screens/LessonScreen";
import MyKnowledge from "./screens/MyKnowledge";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<CreateFamily />} />
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/familia" element={<Navigate to="/familia/explorar" replace />} />
        <Route path="/familia/explorar" element={<WhoExplores />} />
        <Route path="/familia/nuevo" element={<AddExplorer />} />
        <Route path="/explorar/:childId" element={<ChildAccess />} />
        <Route path="/jugar" element={<Spark />} />
        <Route path="/jugar/leccion/:id" element={<LessonScreen />} />
        <Route path="/jugar/mis-islas" element={<MyKnowledge />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
```

## Step 6: Toda la suite + lint
`npm test` → todo PASS. `npm run lint` → limpio.

## Step 7: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): My Knowledge (archipelago) + wire child world flow"
```
