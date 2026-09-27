import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { ApiError, apiFetch, assetUrl, getToken, setToken } from "./client";

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
  const spy = vi.fn<(url: string, init?: RequestInit) => Promise<Response>>(async () => new Response("{}", { status: 200 }));
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

test("apiFetch exposes the Retry-After seconds on a 429", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(JSON.stringify({ detail: "Demasiados intentos." }), {
          status: 429,
          headers: { "Retry-After": "42" },
        }),
    ),
  );
  await expect(apiFetch("/auth/login", { method: "POST" })).rejects.toMatchObject({
    status: 429,
    retryAfter: 42,
  });
});

test("una respuesta que no es JSON da un ApiError con su código, no un SyntaxError", async () => {
  // Pasó en la demo publicada el 27-09: el alta falló con el mensaje genérico
  // «No se pudo crear la cuenta» y el motivo real no llegó nunca a la pantalla.
  // `JSON.parse` corría antes de mirar `res.ok` y sin protección, así que
  // cualquier cuerpo que no fuese JSON —la página de login de Cloudflare Access,
  // un 502 de nginx— reventaba con SyntaxError. Como no es un ApiError, las
  // pantallas caen a su mensaje genérico y esconden la causa.
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response("<!DOCTYPE html><html>Acceso denegado</html>", { status: 502 })),
  );
  const err = (await apiFetch("/auth/register", { method: "POST" }).catch((e) => e)) as ApiError;
  expect(err).toBeInstanceOf(ApiError);
  expect(err.status).toBe(502);
  expect(err.message).toMatch(/502/);
});

test("un 200 con HTML (Access cortando la llamada) explica que la sesión caducó", async () => {
  // El caso más probable en la demo publicada, y el que menos lo parece: `fetch`
  // sigue las redirecciones, así que el 302 de Cloudflare Access hacia su pantalla
  // de login se convierte en un 200 con HTML. `res.ok` es true y el cuerpo no es
  // JSON. Sin este caso, el adulto ve «No se pudo crear la cuenta» cuando lo único
  // que le pasa es que tiene que recargar.
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response("<!DOCTYPE html><html>Log in to chispa</html>", { status: 200 })),
  );
  const err = (await apiFetch("/auth/register", { method: "POST" }).catch((e) => e)) as ApiError;
  expect(err).toBeInstanceOf(ApiError);
  expect(err.message).toMatch(/sesión/i);
  expect(err.message).toMatch(/recarga/i);
});

test("las peticiones van al mismo origen bajo /api, sin host horneado en el bundle", async () => {
  const spy = vi.fn<(url: string, init?: RequestInit) => Promise<Response>>(
    async () => new Response("{}", { status: 200 }),
  );
  vi.stubGlobal("fetch", spy);

  await apiFetch("/auth/login", { method: "POST" });

  expect(spy.mock.calls[0][0]).toBe("/api/auth/login");
});

test("las imágenes generadas también salen por el mismo origen", () => {
  expect(assetUrl("/media/lessons/8.png")).toBe("/api/media/lessons/8.png");
});

test("una VITE_API_URL vacía no deja la base en blanco: sigue siendo /api", async () => {
  // El Dockerfile define la variable como cadena vacía cuando no se quiere un
  // backend ajeno. Con `??` eso NO caía al valor por defecto y las peticiones
  // salían a /auth/register, que nginx sirve como fichero estático: 405.
  vi.resetModules();
  vi.stubEnv("VITE_API_URL", "");
  const spy = vi.fn<(url: string, init?: RequestInit) => Promise<Response>>(
    async () => new Response("{}", { status: 200 }),
  );
  vi.stubGlobal("fetch", spy);
  const { apiFetch: recargado } = await import("./client");
  await recargado("/auth/register", { method: "POST" });
  expect(spy.mock.calls[0][0]).toBe("/api/auth/register");
  vi.unstubAllEnvs();
});
