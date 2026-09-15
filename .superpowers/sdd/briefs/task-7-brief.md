# Task 7: Añadir explorador, elegir explorador y acceso del niño con PIN

Estas son tus REQUISITOS. Usa el código EXACTO que aparece aquí.

**Files:**
- Create: `frontend/src/api/children.ts`
- Create: `frontend/src/screens/AddExplorer.tsx`
- Create: `frontend/src/screens/WhoExplores.tsx`
- Create: `frontend/src/screens/ChildAccess.tsx`
- Modify: `frontend/src/App.tsx` (rutas nuevas)
- Test: `frontend/src/screens/WhoExplores.test.tsx`
- Test: `frontend/src/screens/ChildAccess.test.tsx`

**Consumes:** `apiFetch` (`../api/client`); `TokenResponse` (`../api/auth`); `Button`, `ScreenCard`; `setToken` (`../api/client`); router.
**Produces:**
- `listChildren(): Promise<Child[]>` (GET `/children`, auth); `Child = { id; name; birthdate; age }`.
- `createChild(name, birthdate, pin): Promise<Child>` (POST `/children`, auth).
- `childLogin(childId, pin): Promise<TokenResponse>` (POST `/children/{id}/login`, auth).
- Rutas protegidas: `/familia/nuevo` (AddExplorer), `/familia/explorar` (WhoExplores), `/explorar/:childId` (ChildAccess con teclado PIN).

- [ ] **Step 1: Crear `frontend/src/api/children.ts`**

```ts
import { apiFetch } from "./client";
import type { TokenResponse } from "./auth";

export type Child = { id: number; name: string; birthdate: string; age: number };

export function listChildren() {
  return apiFetch<Child[]>("/children", { auth: true });
}

export function createChild(name: string, birthdate: string, pin: string) {
  return apiFetch<Child>("/children", {
    method: "POST",
    auth: true,
    body: { name, birthdate, pin },
  });
}

export function childLogin(childId: number, pin: string) {
  return apiFetch<TokenResponse>(`/children/${childId}/login`, {
    method: "POST",
    auth: true,
    body: { pin },
  });
}
```

- [ ] **Step 2: Escribir el test `frontend/src/screens/WhoExplores.test.tsx`**

```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import WhoExplores from "./WhoExplores";

beforeEach(() => localStorage.clear());
afterEach(() => vi.restoreAllMocks());

test("lists the crew (children) from the API", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(
          JSON.stringify([
            { id: 1, name: "Leo", birthdate: "2019-03-12", age: 7 },
            { id: 2, name: "Mía", birthdate: "2020-01-01", age: 6 },
          ]),
          { status: 200 },
        ),
    ),
  );
  render(
    <MemoryRouter>
      <WhoExplores />
    </MemoryRouter>,
  );
  expect(await screen.findByText("Leo")).toBeInTheDocument();
  expect(screen.getByText("Mía")).toBeInTheDocument();
});
```

- [ ] **Step 3: Crear `frontend/src/screens/WhoExplores.tsx`**

```tsx
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { listChildren, type Child } from "../api/children";
import ScreenCard from "../components/ScreenCard";

export default function WhoExplores() {
  const [children, setChildren] = useState<Child[]>([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    listChildren()
      .then(setChildren)
      .catch(() => setError("No se pudo cargar la tripulación"));
  }, []);

  return (
    <ScreenCard>
      <h1 style={{ fontFamily: "var(--font-head)" }}>¿Quién va a explorar?</h1>
      {error && <p role="alert">{error}</p>}
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {children.map((c) => (
          <button
            key={c.id}
            onClick={() => navigate(`/explorar/${c.id}`)}
            style={{ textAlign: "left", borderRadius: 22, padding: 16 }}
          >
            <strong>{c.name}</strong>
            <div>{c.age} años</div>
          </button>
        ))}
        <Link to="/familia/nuevo">＋ Añadir explorador</Link>
      </div>
    </ScreenCard>
  );
}
```

- [ ] **Step 4: Crear `frontend/src/screens/AddExplorer.tsx`**

```tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createChild } from "../api/children";
import { ApiError } from "../api/client";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

function ageFrom(birthdate: string): number | null {
  if (!birthdate) return null;
  const b = new Date(birthdate);
  const t = new Date();
  let age = t.getFullYear() - b.getFullYear();
  const m = t.getMonth() - b.getMonth();
  if (m < 0 || (m === 0 && t.getDate() < b.getDate())) age--;
  return age;
}

export default function AddExplorer() {
  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const age = ageFrom(birthdate);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await createChild(name, birthdate, pin);
      navigate("/familia/explorar");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar");
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <h1 style={{ fontFamily: "var(--font-head)" }}>Nuevo explorador</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <label>
          Alias
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Fecha de nacimiento
          <input
            type="date"
            value={birthdate}
            onChange={(e) => setBirthdate(e.target.value)}
            required
          />
        </label>
        {age !== null && <div aria-label="edad calculada">{age} años</div>}
        <label>
          Clave secreta (PIN)
          <input
            inputMode="numeric"
            pattern="[0-9]*"
            minLength={4}
            maxLength={8}
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            required
          />
        </label>
        {error && <p role="alert">{error}</p>}
        <Button type="submit" disabled={busy}>
          Guardar explorador
        </Button>
      </form>
    </ScreenCard>
  );
}
```

- [ ] **Step 5: Escribir el test `frontend/src/screens/ChildAccess.test.tsx`**

```tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import ChildAccess from "./ChildAccess";

beforeEach(() => localStorage.clear());
afterEach(() => vi.restoreAllMocks());

test("typing 4 digits logs the child in and stores token", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(JSON.stringify({ access_token: "child-tok", token_type: "bearer" }), {
          status: 200,
        }),
    ),
  );
  render(
    <MemoryRouter initialEntries={["/explorar/1"]}>
      <Routes>
        <Route path="/explorar/:childId" element={<ChildAccess />} />
      </Routes>
    </MemoryRouter>,
  );
  for (const d of ["1", "2", "3", "4"]) {
    await userEvent.click(screen.getByRole("button", { name: d }));
  }
  await waitFor(() => expect(localStorage.getItem("chispa_token")).toBe("child-tok"));
});
```

- [ ] **Step 6: Crear `frontend/src/screens/ChildAccess.tsx`**

```tsx
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { childLogin } from "../api/children";
import { setToken } from "../api/client";
import ScreenCard from "../components/ScreenCard";

export default function ChildAccess() {
  const { childId } = useParams();
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (pin.length === 4 && childId) {
      childLogin(Number(childId), pin)
        .then((res) => setToken(res.access_token))
        .catch(() => {
          setError("Clave incorrecta");
          setPin("");
        });
    }
  }, [pin, childId]);

  const keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "⌫"];

  return (
    <ScreenCard>
      <h1 style={{ fontFamily: "var(--font-head)" }}>Pon tu clave para zarpar</h1>
      <div aria-label="pin" style={{ display: "flex", gap: 14, justifyContent: "center" }}>
        {[0, 1, 2, 3].map((i) => (
          <span
            key={i}
            style={{
              width: 14,
              height: 14,
              borderRadius: 99,
              background: i < pin.length ? "var(--coral)" : "rgba(255,255,255,.5)",
            }}
          />
        ))}
      </div>
      {error && <p role="alert">{error}</p>}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 14, marginTop: 20 }}>
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

- [ ] **Step 7: Actualizar `frontend/src/App.tsx`** (contenido completo)

```tsx
import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./routes/ProtectedRoute";
import CreateFamily from "./screens/CreateFamily";
import Login from "./screens/Login";
import AddExplorer from "./screens/AddExplorer";
import WhoExplores from "./screens/WhoExplores";
import ChildAccess from "./screens/ChildAccess";

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
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
```

Nota: `/familia` ahora redirige a `/familia/explorar` (¿quién explora?), que es el destino tras registro/login. NO cambies `App.test.tsx` (sigue comprobando la pantalla raíz CreateFamily, que se mantiene).

- [ ] **Step 8: Ejecutar toda la suite**

Run (desde `frontend/`): `npm test`
Expected: todos PASS.

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): add explorer, crew selection and child PIN access"
```
