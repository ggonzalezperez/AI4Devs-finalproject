const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "chispa_token";
const CHILD_TOKEN_KEY = "chispa_child_token";

export function setChildToken(token: string | null): void {
  if (token) localStorage.setItem(CHILD_TOKEN_KEY, token);
  else localStorage.removeItem(CHILD_TOKEN_KEY);
}

export function getChildToken(): string | null {
  return localStorage.getItem(CHILD_TOKEN_KEY);
}

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

type Options = { method?: string; body?: unknown; auth?: boolean | "child" };

export function assetUrl(path: string): string {
  return `${BASE_URL}${path}`;
}

// Sesión caducada/ inválida: limpia el token y vuelve a autenticar. Solo se llama
// cuando el 401 es por el TOKEN (no por un PIN o credenciales incorrectos), para no
// desloguear al padre cuando un niño falla el PIN.
function handleExpiredSession(auth: boolean | "child"): void {
  if (auth === "child") setChildToken(null);
  else setToken(null);
  const target = auth === "child" ? "/familia/explorar" : "/login";
  if (typeof window !== "undefined" && window.location.pathname !== target) {
    try {
      window.location.assign(target);
    } catch {
      /* entorno sin navegación (p. ej. tests) */
    }
  }
}

export async function apiFetch<T>(path: string, options: Options = {}): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (options.auth) {
    const token = options.auth === "child" ? getChildToken() : getToken();
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
    if (res.status === 401 && options.auth && /token/i.test(String(detail))) {
      handleExpiredSession(options.auth);
    }
    throw new ApiError(res.status, detail);
  }
  return data as T;
}
