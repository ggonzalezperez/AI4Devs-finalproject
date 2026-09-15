# Task B1: Cliente API del niño (núcleo)

Usa el código EXACTO. Frontend `frontend/`. Rama `feature-entrega3-nucleo`. SIN push.
NOTA: esta tarea SOLO crea el cliente API y su test. Las rutas y pantallas se añaden en B2–B4 (no toques `App.tsx` aquí).

**Files:**
- Create: `frontend/src/api/nucleo.ts`
- Test: `frontend/src/api/nucleo.test.ts`

## Step 1: Test `frontend/src/api/nucleo.test.ts`

```ts
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { createLesson, getSuggestions } from "./nucleo";
import { setToken } from "./client";

beforeEach(() => {
  localStorage.clear();
  setToken("child-tok");
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
  const init = spy.mock.calls[0][1] as RequestInit;
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
```

## Step 2: Crear `frontend/src/api/nucleo.ts`

```ts
import { apiFetch } from "./client";

export type Lesson = {
  id: number;
  curiosity: string;
  subject: string;
  concept: string;
  title: string;
  body: string;
  fun_fact: string;
  answered: boolean;
  quiz: { question: string; options: string[] };
};

export type Suggestion = { curiosity: string; emoji: string };
export type AnswerResult = { correct: boolean; explanation: string; concept: string };
export type KnowledgeNode = { id: number; concept: string; subject: string; mastery: number };

export function createLesson(curiosity: string, subject?: string) {
  return apiFetch<Lesson>("/lessons", { method: "POST", auth: true, body: { curiosity, subject } });
}

export function getLesson(id: number) {
  return apiFetch<Lesson>(`/lessons/${id}`, { auth: true });
}

export function answerLesson(id: number, choiceIndex: number) {
  return apiFetch<AnswerResult>(`/lessons/${id}/answer`, {
    method: "POST",
    auth: true,
    body: { choice_index: choiceIndex },
  });
}

export function getSuggestions() {
  return apiFetch<Suggestion[]>("/me/suggestions", { auth: true });
}

export function getKnowledge() {
  return apiFetch<KnowledgeNode[]>("/me/knowledge", { auth: true });
}
```

## Step 3: Test + suite
`npm test src/api/nucleo.test.ts` → PASS. Luego `npm test` completo → todo PASS.

## Step 4: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): nucleo API client"
```
