# Task 4: API de auth + contexto de sesión

Estas son tus REQUISITOS. Usa el código EXACTO que aparece aquí.

**Files:**
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/auth/SessionContext.tsx`
- Test: `frontend/src/auth/SessionContext.test.tsx`

**Consumes:** `apiFetch`, `setToken`, `getToken` de `../api/client` (ya existe).
**Produces:**
- `registerFamily(name, email, password): Promise<TokenResponse>` → POST `/auth/register`.
- `loginFamily(email, password): Promise<TokenResponse>` → POST `/auth/login`.
- `type TokenResponse = { access_token: string; token_type: string }`.
- `useSession()` → `{ isAuthenticated, login(token), logout() }`; `<SessionProvider>`.

- [ ] **Step 1: Crear `frontend/src/api/auth.ts`**

```ts
import { apiFetch } from "./client";

export type TokenResponse = { access_token: string; token_type: string };

export function registerFamily(name: string, email: string, password: string) {
  return apiFetch<TokenResponse>("/auth/register", {
    method: "POST",
    body: { name, email, password },
  });
}

export function loginFamily(email: string, password: string) {
  return apiFetch<TokenResponse>("/auth/login", {
    method: "POST",
    body: { email, password },
  });
}
```

- [ ] **Step 2: Escribir el test `frontend/src/auth/SessionContext.test.tsx`**

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, test } from "vitest";
import { SessionProvider, useSession } from "./SessionContext";

function Probe() {
  const { isAuthenticated, login, logout } = useSession();
  return (
    <div>
      <span>{isAuthenticated ? "in" : "out"}</span>
      <button onClick={() => login("tok")}>login</button>
      <button onClick={logout}>logout</button>
    </div>
  );
}

beforeEach(() => localStorage.clear());

test("login and logout toggle authentication", async () => {
  render(
    <SessionProvider>
      <Probe />
    </SessionProvider>,
  );
  expect(screen.getByText("out")).toBeInTheDocument();
  await userEvent.click(screen.getByText("login"));
  expect(screen.getByText("in")).toBeInTheDocument();
  await userEvent.click(screen.getByText("logout"));
  expect(screen.getByText("out")).toBeInTheDocument();
});
```

- [ ] **Step 3: Ejecutar y verificar que falla**

Run (desde `frontend/`): `npm test src/auth/SessionContext.test.tsx`
Expected: FAIL (módulo no existe).

- [ ] **Step 4: Crear `frontend/src/auth/SessionContext.tsx`**

```tsx
import { createContext, useCallback, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { getToken, setToken } from "../api/client";

type Session = {
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
};

const SessionCtx = createContext<Session | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [token, setTok] = useState<string | null>(getToken());

  const login = useCallback((t: string) => {
    setToken(t);
    setTok(t);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setTok(null);
  }, []);

  const value = useMemo(
    () => ({ isAuthenticated: token !== null, login, logout }),
    [token, login, logout],
  );

  return <SessionCtx.Provider value={value}>{children}</SessionCtx.Provider>;
}

export function useSession(): Session {
  const ctx = useContext(SessionCtx);
  if (!ctx) throw new Error("useSession must be used within SessionProvider");
  return ctx;
}
```

- [ ] **Step 5: Ejecutar y verificar que pasa**

Run (desde `frontend/`): `npm test src/auth/SessionContext.test.tsx`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): auth API and session context"
```
