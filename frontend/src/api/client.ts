// Mismo origen: nginx enruta /api al backend. Antes aquí se horneaba un host
// absoluto en tiempo de build, y eso ataba el bundle a una máquina concreta: al
// abrir la app desde el móvil por la IP de casa, seguía llamando a localhost y
// no funcionaba nada hasta reconstruir. Además una página https no puede llamar
// a un backend http, así que el host absoluto impedía servir la app con TLS.
// Se puede sobreescribir con VITE_API_URL para apuntar a otro backend.
//
// Ojo con el operador: `??` solo cubre undefined, y el Dockerfile define la
// variable como cadena VACÍA cuando no hay backend ajeno. Con `??` la base
// quedaba en "" y las peticiones salían a /auth/register, que nginx sirve como
// fichero estático y responde 405. Hace falta tratar la cadena vacía.
const BASE_URL = import.meta.env.VITE_API_URL?.trim() || "/api";
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
  /** Segundos que pide esperar el servidor en un 429. */
  retryAfter?: number;
  constructor(status: number, message: string, retryAfter?: number) {
    super(message);
    this.status = status;
    this.retryAfter = retryAfter;
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
  // El cuerpo puede no ser JSON, y entonces `JSON.parse` lanza un SyntaxError.
  // Como no es un ApiError, las pantallas caen a su mensaje genérico («No se pudo
  // crear la cuenta») y el motivo real no llega nunca al adulto. Pasó en la demo
  // publicada el 27-09-2026.
  //
  // El caso que más importa no es un error HTTP: `fetch` sigue las redirecciones,
  // así que cuando Cloudflare Access corta una llamada a /api por sesión caducada,
  // el 302 acaba siendo un 200 con la página de login en HTML. De ahí que se trate
  // también `res.ok`.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- lo que devolvía
  // `JSON.parse` antes de envolverlo; mantenerlo evita cambiar nada más.
  let data: any = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    throw new ApiError(
      res.status,
      res.ok
        ? "El servidor respondió algo que no se pudo entender. Puede que tu sesión haya caducado: recarga la página."
        : `El servidor respondió algo inesperado (Error ${res.status}).`,
    );
  }
  if (!res.ok) {
    const detail = data?.detail ?? `Error ${res.status}`;
    if (res.status === 401 && options.auth && /token/i.test(String(detail))) {
      handleExpiredSession(options.auth);
    }
    const retryAfter = Number(res.headers.get("Retry-After"));
    throw new ApiError(res.status, detail, Number.isFinite(retryAfter) && retryAfter > 0 ? retryAfter : undefined);
  }
  return data as T;
}
