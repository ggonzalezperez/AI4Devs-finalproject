# Task B1b: Lecciones conversacionales (frontend) — chips de "seguir preguntando"

Frontend `frontend/`. Rama `feature-lecciones-ricas`. SIN push (lo hace el controlador).
B1a (backend) ya devuelve `follow_ups: string[]` en la lección. Aquí los mostramos como chips: al pulsarlos se crea una nueva lección con esa pregunta → sensación de conversación ("seguir preguntando para descubrir").

**Files:**
- Modify: `frontend/src/api/nucleo.ts` (tipo Lesson + follow_ups)
- Modify: `frontend/src/screens/LessonScreen.tsx` (chips + arrancar lección de continuación)
- Modify: `frontend/src/i18n/translations.ts` (`lesson.more`)
- Modify test: `frontend/src/screens/LessonScreen.test.tsx`

## Step 1: `frontend/src/api/nucleo.ts`
En el tipo `Lesson`, añade el campo (junto a `quiz`):
```ts
  follow_ups: string[];
```

## Step 2: i18n — `frontend/src/i18n/translations.ts`
es: `"lesson.more": "¿Quieres saber más?",`
en: `"lesson.more": "Want to know more?",`

## Step 3: `frontend/src/screens/LessonScreen.tsx`
Reemplaza el contenido por esta versión (añade `createLesson` al import, estado `busy`, reseteo al cambiar de `id`, helper `startFollowUp`, y los chips en la vista de lección y en la de acierto):
```tsx
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { answerLesson, createLesson, getLesson, type AnswerResult, type Lesson } from "../api/nucleo";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";
import ChildHeader from "../components/ChildHeader";

export default function LessonScreen() {
  const { id } = useParams();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [playing, setPlaying] = useState(false);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [busy, setBusy] = useState(false);
  const { t } = useI18n();
  const navigate = useNavigate();

  useEffect(() => {
    // Al cambiar de lección (incluido seguir una pregunta), reinicia el estado.
    setLesson(null);
    setPlaying(false);
    setResult(null);
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

  async function startFollowUp(question: string) {
    setBusy(true);
    try {
      const next = await createLesson(question);
      navigate(`/jugar/leccion/${next.id}`);
    } catch {
      // silencioso: el niño no ve errores técnicos
    } finally {
      setBusy(false);
    }
  }

  const followUps = lesson.follow_ups ?? [];
  const moreChips =
    followUps.length > 0 ? (
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        <div style={{ fontWeight: 800, color: "#0a5a53" }}>{t("lesson.more")}</div>
        {followUps.map((q) => (
          <button
            key={q}
            onClick={() => void startFollowUp(q)}
            disabled={busy}
            style={{ textAlign: "left", padding: 12 }}
          >
            🔎 {q}
          </button>
        ))}
      </div>
    ) : null;

  return (
    <ScreenCard>
      {!playing ? (
        <>
          <ChildHeader />
          <div style={{ fontSize: 12, fontWeight: 800, textTransform: "uppercase", color: "#0a5a53" }}>
            {lesson.subject}
          </div>
          <h1>{lesson.title}</h1>
          <div style={{ background: "#fff", borderRadius: 16, padding: 16, lineHeight: 1.6, fontSize: 16, color: "var(--teal-dark)" }}>
            {lesson.body}
          </div>
          <div style={{ background: "#fff", borderRadius: 16, padding: 14 }}>
            <strong style={{ color: "var(--amber)" }}>💡 {t("lesson.funFact")}</strong>
            <div>{lesson.fun_fact}</div>
          </div>
          <Button onClick={() => setPlaying(true)}>{t("lesson.play")}</Button>
          {moreChips}
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
            <>
              <Button onClick={() => navigate("/jugar/mis-islas")}>{t("lesson.toIslands")}</Button>
              {moreChips}
            </>
          ) : (
            <Button onClick={() => setResult(null)}>↺</Button>
          )}
        </>
      )}
    </ScreenCard>
  );
}
```

## Step 4: Test `frontend/src/screens/LessonScreen.test.tsx`
Lee el test actual. El mock de `getLesson` (respuesta de `/lessons/{id}`) debe incluir ahora `follow_ups` (si no, TypeScript falla). Añade `follow_ups: ["¿Por qué llueve?", "¿Me das un ejemplo?"]` al JSON de la lección mockeada. Mantén verdes las aserciones existentes y añade una nueva:
```tsx
expect(await screen.findByText(/¿Quieres saber más\?/)).toBeInTheDocument();
expect(screen.getByText(/¿Por qué llueve\?/)).toBeInTheDocument();
```
(Si el test envuelve en `<I18nProvider initialLang="es">`, los textos en español coinciden; si no, ajústalo a ese patrón como el resto de tests.)

## Step 5: Verificación
- `npm test` → todo PASS.
- `npm run lint` → limpio.

## Step 6: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): conversational lesson follow-up chips"
```
