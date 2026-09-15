import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { setToken } from "./client";
import { getChildKnowledge, getChildProfile } from "./children";

beforeEach(() => {
  localStorage.clear();
  setToken("family-tok");
});
afterEach(() => vi.restoreAllMocks());

test("getChildProfile pide la ficha del hijo con el token de familia", async () => {
  const fetchMock = vi.fn(
    async (_url: string, _init?: RequestInit) =>
      new Response(
        JSON.stringify({ name: "Nora", age: 7, islands: 2, avatar: "fox", avatar_image_url: null }),
        { status: 200 },
      ),
  );
  vi.stubGlobal("fetch", fetchMock);

  const perfil = await getChildProfile(1);

  expect(perfil.name).toBe("Nora");
  expect(perfil.islands).toBe(2);
  const [url, init] = fetchMock.mock.calls[0];
  expect(String(url)).toContain("/children/1/profile");
  expect(init?.headers).toMatchObject({ Authorization: "Bearer family-tok" });
});

test("getChildKnowledge pide el archipiélago del hijo", async () => {
  const fetchMock = vi.fn(
    async (_url: string, _init?: RequestInit) =>
      new Response(
        JSON.stringify([{ id: 10, concept: "flotabilidad", subject: "ciencia", mastery: 3, root_lesson_id: 9 }]),
        { status: 200 },
      ),
  );
  vi.stubGlobal("fetch", fetchMock);

  const ficha = await getChildKnowledge(1);

  expect(ficha).toHaveLength(1);
  expect(ficha[0].concept).toBe("flotabilidad");
  expect(String(fetchMock.mock.calls[0][0])).toContain("/children/1/knowledge");
});
