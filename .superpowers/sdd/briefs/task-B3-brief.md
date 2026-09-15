# Task B3: Pantalla de Lección y Reto (quiz)

Usa el código EXACTO. Frontend `frontend/`. Rama `feature-entrega3-nucleo`. SIN push.

**Files:**
- Create: `frontend/src/screens/LessonScreen.tsx`
- Modify: `frontend/src/i18n/translations.ts` (añadir claves a es y en)
- Test: `frontend/src/screens/LessonScreen.test.tsx`

## Step 1: Añadir claves i18n en `translations.ts` (es y en), sin tocar existentes

es:
```
    "lesson.play": "¡A jugar! →",
    "lesson.funFact": "Dato sorprendente",
    "lesson.correct": "¡Muy bien!",
    "lesson.wrong": "¡Casi! Inténtalo otra vez",
    "lesson.toIslands": "Ver mis islas 🗺️",
```
en:
```
    "lesson.play": "Let's play! →",
    "lesson.funFact": "Surprising fact",
    "lesson.correct": "Great job!",
    "lesson.wrong": "Almost! Try again",
    "lesson.toIslands": "See my islands 🗺️",
```

## Step 2: Test `frontend/src/screens/LessonScreen.test.tsx`

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setToken } from "../api/client";
import LessonScreen from "./LessonScreen";

beforeEach(() => {
  localStorage.clear();
  setToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

function renderAt(id: number) {
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter initialEntries={[`/jugar/leccion/${id}`]}>
        <Routes>
          <Route path="/jugar/leccion/:id" element={<LessonScreen />} />
        </Routes>
      </MemoryRouter>
    </I18nProvider>,
  );
}

test("shows lesson then quiz, and feedback on answer", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (_url: string, init?: RequestInit) => {
      if (init?.method === "POST") {
        return new Response(JSON.stringify({ correct: true, explanation: "¡bien!", concept: "c" }), { status: 200 });
      }
      return new Response(
        JSON.stringify({
          id: 7, curiosity: "x", subject: "ciencia", concept: "c", title: "La lluvia",
          body: "El agua sube y baja", fun_fact: "dato", answered: false,
          quiz: { question: "¿Qué cae?", options: ["sol", "agua", "viento"] },
        }),
        { status: 200 },
      );
    }),
  );
  renderAt(7);
  expect(await screen.findByText("La lluvia")).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: /jugar/i }));
  await userEvent.click(screen.getByRole("button", { name: "agua" }));
  expect(await screen.findByText(/bien/i)).toBeInTheDocument();
});
```

## Step 3: Crear `frontend/src/screens/LessonScreen.tsx`

```tsx
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { answerLesson, getLesson, type AnswerResult, type Lesson } from "../api/nucleo";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

export default function LessonScreen() {
  const { id } = useParams();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [playing, setPlaying] = useState(false);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const { t } = useI18n();
  const navigate = useNavigate();

  useEffect(() => {
    if (id) getLesson(Number(id)).then(setLesson).catch(() => undefined);
  }, [id]);

  if (!lesson) {
    return (
      <ScreenCard>
        <p>…</p>
      </ScreenCard>
    );
  }

  async function choose(i: number) {
    if (!lesson) return;
    const r = await answerLesson(lesson.id, i);
    setResult(r);
  }

  return (
    <ScreenCard>
      {!playing ? (
        <>
          <div style={{ fontSize: 12, fontWeight: 800, textTransform: "uppercase", color: "#0a5a53" }}>
            {lesson.subject}
          </div>
          <h1>{lesson.title}</h1>
          <p style={{ lineHeight: 1.5 }}>{lesson.body}</p>
          <div style={{ background: "#fff", borderRadius: 16, padding: 14 }}>
            <strong style={{ color: "var(--amber)" }}>💡 {t("lesson.funFact")}</strong>
            <div>{lesson.fun_fact}</div>
          </div>
          <Button onClick={() => setPlaying(true)}>{t("lesson.play")}</Button>
        </>
      ) : !result ? (
        <>
          <h1>{lesson.quiz.question}</h1>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {lesson.quiz.options.map((opt, i) => (
              <button key={opt} onClick={() => void choose(i)} style={{ padding: 16 }}>
                {opt}
              </button>
            ))}
          </div>
        </>
      ) : (
        <>
          <div style={{ fontSize: 60, textAlign: "center" }}>{result.correct ? "🎉" : "💪"}</div>
          <h1 style={{ textAlign: "center" }}>{result.correct ? t("lesson.correct") : t("lesson.wrong")}</h1>
          <p style={{ textAlign: "center" }}>{result.explanation}</p>
          {result.correct ? (
            <Button onClick={() => navigate("/jugar/mis-islas")}>{t("lesson.toIslands")}</Button>
          ) : (
            <Button onClick={() => setResult(null)}>↺</Button>
          )}
        </>
      )}
    </ScreenCard>
  );
}
```

## Step 4: Test + suite + lint
`npm test src/screens/LessonScreen.test.tsx` → PASS. Luego `npm test` y `npm run lint` → todo verde.

## Step 5: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): Lesson + quiz screen with feedback"
```
