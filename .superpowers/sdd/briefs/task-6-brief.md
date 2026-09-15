# Task 6: Pantallas de crear familia y login

Estas son tus REQUISITOS. Usa el código EXACTO que aparece aquí.

**Files:**
- Create: `frontend/src/screens/CreateFamily.tsx`
- Create: `frontend/src/screens/Login.tsx`
- Modify: `frontend/src/App.tsx` (usar pantallas reales)
- Test: `frontend/src/screens/CreateFamily.test.tsx`

**Consumes:** `registerFamily`, `loginFamily` (`../api/auth`); `useSession` (`../auth/SessionContext`); `Button`, `ScreenCard` (`../components/*`); `ApiError` (`../api/client`); `useNavigate`, `Link` (react-router-dom).
**Produces:** ruta `/` → `CreateFamily`; `/login` → `Login`. Al éxito llaman `login(token)` y navegan a `/familia`. Muestran error de `ApiError`.

- [ ] **Step 1: Escribir el test `frontend/src/screens/CreateFamily.test.tsx`**

```tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { SessionProvider } from "../auth/SessionContext";
import CreateFamily from "./CreateFamily";

beforeEach(() => localStorage.clear());
afterEach(() => vi.restoreAllMocks());

function setup() {
  render(
    <SessionProvider>
      <MemoryRouter>
        <CreateFamily />
      </MemoryRouter>
    </SessionProvider>,
  );
}

test("submits registration and stores token", async () => {
  const fetchMock = vi.fn(
    async () =>
      new Response(JSON.stringify({ access_token: "t1", token_type: "bearer" }), {
        status: 201,
      }),
  );
  vi.stubGlobal("fetch", fetchMock);
  setup();
  await userEvent.type(screen.getByLabelText(/tu nombre/i), "Ana");
  await userEvent.type(screen.getByLabelText(/email/i), "ana@x.com");
  await userEvent.type(screen.getByLabelText(/contraseña/i), "secret123");
  await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
  await waitFor(() => expect(localStorage.getItem("chispa_token")).toBe("t1"));
});

test("shows error message when email already exists", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(JSON.stringify({ detail: "Email ya registrado" }), { status: 409 }),
    ),
  );
  setup();
  await userEvent.type(screen.getByLabelText(/tu nombre/i), "Ana");
  await userEvent.type(screen.getByLabelText(/email/i), "dup@x.com");
  await userEvent.type(screen.getByLabelText(/contraseña/i), "secret123");
  await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
  expect(await screen.findByText(/email ya registrado/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run (desde `frontend/`): `npm test src/screens/CreateFamily.test.tsx`
Expected: FAIL (módulo no existe).

- [ ] **Step 3: Crear `frontend/src/screens/CreateFamily.tsx`**

```tsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerFamily } from "../api/auth";
import { ApiError } from "../api/client";
import { useSession } from "../auth/SessionContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

export default function CreateFamily() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { login } = useSession();
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { access_token } = await registerFamily(name, email, password);
      login(access_token);
      navigate("/familia");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo crear la cuenta");
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <h1 style={{ fontFamily: "var(--font-head)", color: "var(--teal-dark)" }}>
        ⚓ Crea el espacio de tu familia
      </h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <label>
          Tu nombre
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Contraseña
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p role="alert" style={{ color: "#b23" }}>{error}</p>}
        <Button type="submit" disabled={busy}>
          Crear cuenta
        </Button>
      </form>
      <p style={{ textAlign: "center" }}>
        ¿Ya navegas con nosotros? <Link to="/login">Entrar</Link>
      </p>
    </ScreenCard>
  );
}
```

- [ ] **Step 4: Crear `frontend/src/screens/Login.tsx`**

```tsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginFamily } from "../api/auth";
import { ApiError } from "../api/client";
import { useSession } from "../auth/SessionContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { login } = useSession();
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { access_token } = await loginFamily(email, password);
      login(access_token);
      navigate("/familia");
    } catch (err) {
      setError(err instanceof ApiError ? "Email o contraseña incorrectos" : "Error al entrar");
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <h1 style={{ fontFamily: "var(--font-head)", color: "var(--teal-dark)" }}>⚓ Entrar</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Contraseña
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p role="alert" style={{ color: "#b23" }}>{error}</p>}
        <Button type="submit" disabled={busy}>
          Entrar
        </Button>
      </form>
      <p style={{ textAlign: "center" }}>
        ¿Nuevo? <Link to="/">Crear cuenta</Link>
      </p>
    </ScreenCard>
  );
}
```

- [ ] **Step 5: Actualizar `frontend/src/App.tsx`** (contenido completo)

```tsx
import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./routes/ProtectedRoute";
import CreateFamily from "./screens/CreateFamily";
import Login from "./screens/Login";

function FamilyHomePlaceholder() {
  return <h1>Panel de familia</h1>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<CreateFamily />} />
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/familia" element={<FamilyHomePlaceholder />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
```

- [ ] **Step 6: Actualizar `frontend/src/App.test.tsx`** (contenido completo)

```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { SessionProvider } from "./auth/SessionContext";
import App from "./App";

test("shows create-family screen at root", () => {
  localStorage.clear();
  render(
    <SessionProvider>
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>
    </SessionProvider>,
  );
  expect(screen.getByText(/crea el espacio de tu familia/i)).toBeInTheDocument();
});
```

- [ ] **Step 7: Ejecutar toda la suite**

Run (desde `frontend/`): `npm test`
Expected: todos PASS.

- [ ] **Step 8: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): create-family and login screens wired to backend"
```
