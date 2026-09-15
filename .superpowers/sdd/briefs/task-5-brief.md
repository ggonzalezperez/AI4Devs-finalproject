# Task 5: Enrutado con rutas protegidas

Estas son tus REQUISITOS. Usa el código EXACTO que aparece aquí.

**Files:**
- Create: `frontend/src/routes/ProtectedRoute.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/main.tsx` (envolver en BrowserRouter + SessionProvider)
- Test: `frontend/src/routes/ProtectedRoute.test.tsx`
- Modify: `frontend/src/App.test.tsx`

**Consumes:** `useSession` de `../auth/SessionContext`; `setToken` de `../api/client`. `react-router-dom` ya está en dependencias.
**Produces:** `<ProtectedRoute>` que redirige a `/login` si no autenticado; `App` con rutas `/login` (público) y `/familia` (protegida, placeholder).

- [ ] **Step 1: Escribir el test `frontend/src/routes/ProtectedRoute.test.tsx`**

```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, expect, test } from "vitest";
import { SessionProvider } from "../auth/SessionContext";
import { setToken } from "../api/client";
import ProtectedRoute from "./ProtectedRoute";

function renderAt(path: string) {
  return render(
    <SessionProvider>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/login" element={<div>login page</div>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/familia" element={<div>panel</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </SessionProvider>,
  );
}

beforeEach(() => localStorage.clear());

test("redirects to /login when not authenticated", () => {
  renderAt("/familia");
  expect(screen.getByText("login page")).toBeInTheDocument();
});

test("renders protected content when authenticated", () => {
  setToken("tok");
  renderAt("/familia");
  expect(screen.getByText("panel")).toBeInTheDocument();
});
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run (desde `frontend/`): `npm test src/routes/ProtectedRoute.test.tsx`
Expected: FAIL (módulo no existe).

- [ ] **Step 3: Crear `frontend/src/routes/ProtectedRoute.tsx`**

```tsx
import { Navigate, Outlet } from "react-router-dom";
import { useSession } from "../auth/SessionContext";

export default function ProtectedRoute() {
  const { isAuthenticated } = useSession();
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}
```

- [ ] **Step 4: Reescribir `frontend/src/App.tsx`** (contenido completo)

```tsx
import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./routes/ProtectedRoute";

function FamilyHomePlaceholder() {
  return <h1>Panel de familia</h1>;
}

function LoginPlaceholder() {
  return <h1>Chispa ✨</h1>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPlaceholder />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/familia" element={<FamilyHomePlaceholder />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
```

- [ ] **Step 5: Actualizar `frontend/src/main.tsx`** (contenido completo)

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./styles/theme.css";
import App from "./App";
import { SessionProvider } from "./auth/SessionContext";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <SessionProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </SessionProvider>
  </StrictMode>,
);
```

- [ ] **Step 6: Actualizar `frontend/src/App.test.tsx`** (contenido completo)

```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { SessionProvider } from "./auth/SessionContext";
import App from "./App";

test("shows login by default when not authenticated", () => {
  localStorage.clear();
  render(
    <SessionProvider>
      <MemoryRouter initialEntries={["/login"]}>
        <App />
      </MemoryRouter>
    </SessionProvider>,
  );
  expect(screen.getByRole("heading", { name: /chispa/i })).toBeInTheDocument();
});
```

- [ ] **Step 7: Ejecutar toda la suite**

Run (desde `frontend/`): `npm test`
Expected: todos PASS.

- [ ] **Step 8: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): routing with protected routes and providers"
```
