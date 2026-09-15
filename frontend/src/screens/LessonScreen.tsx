import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { answerLesson, askInLesson, getThread, type AnswerResult, type Lesson } from "../api/nucleo";
import { assetUrl } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import ScreenCard from "../components/ScreenCard";
import ChildHeader from "../components/ChildHeader";
import MicButton from "../components/MicButton";
import Thinking from "../components/Thinking";
import SpeakButton from "../components/SpeakButton";

function ChatTurn({ turn }: { turn: Lesson }) {
  const { t } = useI18n();
  // La ilustración puede faltar aunque la BD guarde su ruta (p. ej. tras un
  // redespliegue que se llevara MEDIA_DIR). El niño no debe ver el icono de
  // imagen rota: si no carga, simplemente no se muestra.
  const [imagenRota, setImagenRota] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [result, setResult] = useState<AnswerResult | null>(null);

  async function choose(i: number) {
    const r = await answerLesson(turn.id, i);
    setResult(r);
  }

  return (
    <div className="anim-rise" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <div style={{ alignSelf: "flex-end", background: "var(--coral)", color: "#fff", borderRadius: "16px 16px 4px 16px", padding: "10px 14px", maxWidth: "85%", fontWeight: 600 }}>
        {turn.curiosity}
      </div>
      <div style={{ alignSelf: "flex-start", background: "#fff", borderRadius: "16px 16px 16px 4px", padding: 14, maxWidth: "94%", color: "var(--teal-dark)" }}>
        <div style={{ fontSize: 11, fontWeight: 800, textTransform: "uppercase", color: "#0a5a53" }}>✨ {turn.subject}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ fontWeight: 700, fontSize: 16, flex: 1 }}>{turn.title}</div>
          <SpeakButton text={`${turn.title}. ${turn.body} ${turn.fun_fact}`} />
        </div>
        {turn.image_url && !imagenRota && (
          <img
            src={assetUrl(turn.image_url)}
            alt={turn.title}
            onError={() => setImagenRota(true)}
            style={{ width: "100%", borderRadius: 12, margin: "8px 0" }}
          />
        )}
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
          <div className="anim-pop" style={{ marginTop: 10, fontWeight: 700, color: result.correct ? "var(--green)" : "var(--coral)" }}>
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
    if (typeof endRef.current?.scrollIntoView === "function") {
      endRef.current.scrollIntoView({ behavior: "smooth" });
    }
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
        {busy && <Thinking />}
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
            <MicButton onText={setQuestion} disabled={busy} />
            <button type="submit" className="btn-primary" disabled={busy || !question.trim()} style={{ width: "auto", padding: "0 16px", minHeight: 0 }}>
              🔎
            </button>
          </form>
        </div>
      )}
    </ScreenCard>
  );
}
