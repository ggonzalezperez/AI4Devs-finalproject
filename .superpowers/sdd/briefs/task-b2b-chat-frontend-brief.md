# Task B2b: Conversación tipo chat (frontend)

Frontend `frontend/`. Rama `feature-lecciones-ricas`. SIN push.
La pantalla de lección pasa a ser un **chat**: carga el hilo (`GET /lessons/{id}/thread`), muestra cada turno como pregunta del niño + respuesta de Chispa, y abajo el niño sigue preguntando (chips o texto libre) con `POST /lessons/{id}/ask`, que **añade** el turno al chat (sin navegar). El **quiz es opcional por turno** (botón "¿Jugamos un reto?") y al responder se queda **en la conversación**. El acceso a las islas ya está en `ChildHeader` (🏝️).

B2a (backend) ya expone `POST /lessons/{id}/ask` (body `{curiosity}`) → turno nuevo, y `GET /lessons/{id}/thread` → lista de turnos (raíz primero). Las islas se crean solas por detrás.

**Files:**
- Modify: `frontend/src/api/nucleo.ts` (askInLesson + getThread)
- Modify: `frontend/src/screens/LessonScreen.tsx` (reescritura a chat)
- Modify: `frontend/src/i18n/translations.ts` (`lesson.quizCta`)
- Modify test: `frontend/src/screens/LessonScreen.test.tsx`

## Step 1: `frontend/src/api/nucleo.ts`
Añade (mantén `getLesson`, `createLesson`, `answerLesson`):
```ts
export function getThread(lessonId: number) {
  return apiFetch<Lesson[]>(`/lessons/${lessonId}/thread`, { auth: "child" });
}

export function askInLesson(lessonId: number, curiosity: string) {
  return apiFetch<Lesson>(`/lessons/${lessonId}/ask`, {
    method: "POST",
    auth: "child",
    body: { curiosity },
  });
}
```

## Step 2: i18n — `frontend/src/i18n/translations.ts`
es: `"lesson.quizCta": "🎯 ¿Jugamos un reto?",`
en: `"lesson.quizCta": "🎯 Play a challenge?",`

## Step 3: Reescribe `frontend/src/screens/LessonScreen.tsx`
```tsx
import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { answerLesson, askInLesson, getThread, type AnswerResult, type Lesson } from "../api/nucleo";
import { useI18n } from "../i18n/I18nContext";
import ScreenCard from "../components/ScreenCard";
import ChildHeader from "../components/ChildHeader";

function ChatTurn({ turn }: { turn: Lesson }) {
  const { t } = useI18n();
  const [playing, setPlaying] = useState(false);
  const [result, setResult] = useState<AnswerResult | null>(null);

  async function choose(i: number) {
    const r = await answerLesson(turn.id, i);
    setResult(r);
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <div style={{ alignSelf: "flex-end", background: "var(--coral)", color: "#fff", borderRadius: "16px 16px 4px 16px", padding: "10px 14px", maxWidth: "85%", fontWeight: 600 }}>
        {turn.curiosity}
      </div>
      <div style={{ alignSelf: "flex-start", background: "#fff", borderRadius: "16px 16px 16px 4px", padding: 14, maxWidth: "94%", color: "var(--teal-dark)" }}>
        <div style={{ fontSize: 11, fontWeight: 800, textTransform: "uppercase", color: "#0a5a53" }}>✨ {turn.subject}</div>
        <div style={{ lineHeight: 1.55, fontSize: 15, marginTop: 4 }}>{turn.body}</div>
        <div style={{ marginTop: 8, fontSize: 13 }}>
          <strong style={{ color: "var(--amber)" }}>💡 {t("lesson.funFact")}: </strong>
          {turn.fun_fact}
        </div>
        {!playing && !result && (
          <button onClick={() => setPlaying(true)} style={{ marginTop: 10, padding: "8px 12px" }}>
            {t("lesson.quizCta")}
          </button>
        )}
        {playing && !result && (
          <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 8 }}>
            <strong>{turn.quiz.question}</strong>
            {turn.quiz.options.map((opt, i) => (
              <button key={opt} onClick={() => void choose(i)} style={{ padding: 12, textAlign: "left" }}>
                {opt}
              </button>
            ))}
          </div>
        )}
        {result && (
          <div style={{ marginTop: 10, fontWeight: 700, color: result.correct ? "var(--green)" : "var(--coral)" }}>
            {result.correct ? `🎉 ${t("lesson.correct")}` : `💪 ${t("lesson.wrong")}`}
            <div style={{ fontWeight: 400, color: "var(--teal-dark)", marginTop: 4 }}>{result.explanation}</div>
            {!result.correct && (
              <button onClick={() => setResult(null)} style={{ marginTop: 8, padding: "6px 12px" }}>↺</button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function LessonScreen() {
  const { id } = useParams();
  const [thread, setThread] = useState<Lesson[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const { t } = useI18n();
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setThread([]);
    setLoaded(false);
    setQuestion("");
    if (id) {
      getThread(Number(id))
        .then(setThread)
        .catch(() => undefined)
        .finally(() => setLoaded(true));
    }
  }, [id]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [thread.length]);

  const last = thread[thread.length - 1];

  async function ask(q: string) {
    const text = q.trim();
    if (!text || !last) return;
    setBusy(true);
    setQuestion("");
    try {
      const next = await askInLesson(last.id, text);
      setThread((prev) => [...prev, next]);
    } catch {
      // silencioso: el niño no ve errores técnicos
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <ChildHeader />
      {loaded && thread.length === 0 && <p>…</p>}
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {thread.map((turn) => (
          <ChatTurn key={turn.id} turn={turn} />
        ))}
        <div ref={endRef} />
      </div>
      {last && (
        <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 4 }}>
          {(last.follow_ups ?? []).map((q) => (
            <button key={q} onClick={() => void ask(q)} disabled={busy} style={{ textAlign: "left", padding: 10 }}>
              🔎 {q}
            </button>
          ))}
          <form onSubmit={(e) => { e.preventDefault(); void ask(question); }} style={{ display: "flex", gap: 8 }}>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder={t("lesson.askPlaceholder")}
              aria-label={t("lesson.askPlaceholder")}
              disabled={busy}
              style={{ flex: 1 }}
            />
            <button type="submit" className="btn-primary" disabled={busy || !question.trim()} style={{ width: "auto", padding: "0 16px", minHeight: 0 }}>
              🔎
            </button>
          </form>
        </div>
      )}
    </ScreenCard>
  );
}
```
Nota: `endRef.current?.scrollIntoView` puede no existir en jsdom; está protegido con `?.` así que no rompe los tests.

## Step 4: Test `frontend/src/screens/LessonScreen.test.tsx`
Reescríbelo para el chat. Ahora la pantalla llama a `GET /lessons/{id}/thread` (devuelve un ARRAY). Mockea `fetch` para devolver un array con un turno y comprueba que se ve la conversación y un chip de follow-up. Patrón (ajusta el shape del turno a `Lesson`, incluyendo `follow_ups`, `quiz`, etc.):
```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setChildToken } from "../api/client";
import LessonScreen from "./LessonScreen";

beforeEach(() => {
  localStorage.clear();
  setChildToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

const TURN = {
  id: 5,
  curiosity: "¿por qué llueve?",
  subject: "ciencia",
  concept: "lluvia",
  title: "La lluvia",
  body: "El agua sube en forma de vapor y vuelve a caer.",
  fun_fact: "Una nube pesa toneladas.",
  answered: false,
  follow_ups: ["¿Y la nieve?"],
  quiz: { question: "¿Qué sube al cielo?", options: ["El agua", "La arena", "El fuego"] },
};

test("renders the conversation and a follow-up chip", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify([TURN]), { status: 200 })),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter initialEntries={["/jugar/leccion/5"]}>
        <Routes>
          <Route path="/jugar/leccion/:id" element={<LessonScreen />} />
        </Routes>
      </MemoryRouter>
    </I18nProvider>,
  );
  expect(await screen.findByText("La lluvia")).toBeInTheDocument();
  expect(screen.getByText(/El agua sube/)).toBeInTheDocument();
  expect(screen.getByText(/¿Y la nieve\?/)).toBeInTheDocument();
});
```
Si había otras aserciones del test antiguo (título, "¡A jugar!", quiz) que ya no apliquen al chat, sustitúyelas por las nuevas. El objetivo: el chat carga el hilo y muestra la respuesta + un chip.

## Step 5: Verificación
- `npm test` → todo PASS.
- `npm run lint` → limpio.

## Step 6: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): chat-style lesson conversation (thread + ask + optional per-turn quiz)"
```
