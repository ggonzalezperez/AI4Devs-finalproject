import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { createLesson, getSuggestions } from "./nucleo";
import { setChildToken } from "./client";

beforeEach(() => {
  localStorage.clear();
  setChildToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

test("createLesson posts curiosity with auth and returns lesson", async () => {
  const spy = vi.fn(
    async () =>
      new Response(
        JSON.stringify({
          id: 1, curiosity: "¿por qué llueve?", subject: "ciencia", concept: "lluvia",
          title: "La lluvia", body: "...", fun_fact: "...", answered: false,
          quiz: { question: "¿?", options: ["a", "b", "c"] },
        }),
        { status: 201 },
      ),
  );
  vi.stubGlobal("fetch", spy);
  const lesson = await createLesson("¿por qué llueve?");
  expect(lesson.quiz.options).toHaveLength(3);
  const init = (spy.mock.calls[0] as unknown as [string, RequestInit])[1];
  expect((init.headers as Record<string, string>).Authorization).toBe("Bearer child-tok");
});

test("getSuggestions returns list", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify([{ curiosity: "x", emoji: "⛵" }]), { status: 200 })),
  );
  const s = await getSuggestions();
  expect(s[0].emoji).toBe("⛵");
});
