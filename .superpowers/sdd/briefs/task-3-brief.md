# Task 3: Cliente de API tipado + almacenamiento de token

Estas son tus REQUISITOS. Usa el código EXACTO que aparece aquí. Sigue TDD (test primero, verlo fallar, implementar, verlo pasar).

**Files:**
- Create: `frontend/src/api/client.ts`
- Test: `frontend/src/api/client.test.ts`

**Produces:**
- `setToken(token: string | null): void` / `getToken(): string | null` (persisten en `localStorage` bajo `chispa_token`).
- `apiFetch<T>(path, options?: { method?; body?; auth? }): Promise<T>` — fetch a `VITE_API_URL + path`, serializa JSON, añade `Authorization: Bearer` si `auth` y hay token, lanza `ApiError(status, detail)` si no-OK.
- `class ApiError extends Error { status: number }`.

- [ ] **Step 1: Escribir los tests `frontend/src/api/client.test.ts`**

```ts
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { ApiError, apiFetch, getToken, setToken } from "./client";

beforeEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});
afterEach(() => localStorage.clear());

test("stores and reads the token", () => {
  setToken("abc");
  expect(getToken()).toBe("abc");
  setToken(null);
  expect(getToken()).toBeNull();
});

test("apiFetch returns parsed JSON on success", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify({ ok: 1 }), { status: 200 })),
  );
  const data = await apiFetch<{ ok: number }>("/x");
  expect(data.ok).toBe(1);
});

test("apiFetch adds Authorization header when auth and token present", async () => {
  setToken("tok123");
  const spy = vi.fn(async () => new Response("{}", { status: 200 }));
  vi.stubGlobal("fetch", spy);
  await apiFetch("/secure", { auth: true });
  const headers = (spy.mock.calls[0][1] as RequestInit).headers as Record<string, string>;
  expect(headers.Authorization).toBe("Bearer tok123");
});

test("apiFetch throws ApiError with status on failure", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify({ detail: "nope" }), { status: 401 })),
  );
  await expect(apiFetch("/x")).rejects.toMatchObject({ status: 401, message: "nope" });
  await expect(apiFetch("/x")).rejects.toBeInstanceOf(ApiError);
});
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run (desde `frontend/`): `npm test src/api/client.test.ts`
Expected: FAIL (módulo no existe).

- [ ] **Step 3: Crear `frontend/src/api/client.ts`**

```ts
const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "chispa_token";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

export function setToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

type Options = { method?: string; body?: unknown; auth?: boolean };

export async function apiFetch<T>(path: string, options: Options = {}): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (options.auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }
  const res = await fetch(`${BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const detail = data?.detail ?? `Error ${res.status}`;
    throw new ApiError(res.status, detail);
  }
  return data as T;
}
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run (desde `frontend/`): `npm test src/api/client.test.ts`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): typed API client with token storage and ApiError"
```
