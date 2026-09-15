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
