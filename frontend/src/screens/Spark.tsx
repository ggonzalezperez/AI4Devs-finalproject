import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createLesson, getSuggestions, type Suggestion } from "../api/nucleo";
import { ApiError } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";
import ChildHeader from "../components/ChildHeader";
import MicButton from "../components/MicButton";
import Thinking from "../components/Thinking";

export default function Spark() {
  const [curiosity, setCuriosity] = useState("");
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { t } = useI18n();
  const navigate = useNavigate();

  useEffect(() => {
    getSuggestions().then(setSuggestions).catch(() => undefined);
  }, []);

  async function start(text: string) {
    if (!text.trim()) return;
    setError("");
    setBusy(true);
    try {
      const lesson = await createLesson(text);
      navigate(`/jugar/leccion/${lesson.id}`);
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 422 ? t("spark.blocked") : t("createFamily.error"),
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <ChildHeader />
      <h1>{t("spark.title")}</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          void start(curiosity);
        }}
        style={{ display: "flex", flexDirection: "column", gap: 12 }}
      >
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={curiosity}
            onChange={(e) => setCuriosity(e.target.value)}
            placeholder={t("spark.placeholder")}
            aria-label={t("spark.placeholder")}
            style={{ flex: 1 }}
          />
          <MicButton onText={setCuriosity} onAutoSubmit={(texto) => void start(texto)} disabled={busy} />
        </div>
        {error && <p role="alert" style={{ color: "#fff", fontWeight: 700 }}>{error}</p>}
        <Button type="submit" disabled={busy}>
          🧭 {t("spark.discover")}
        </Button>
        {busy && <Thinking />}
      </form>
      <div style={{ fontWeight: 800, color: "#0a5a53", marginTop: 4 }}>{t("spark.suggestions")}</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {suggestions.map((s) => (
          <button key={s.curiosity} onClick={() => void start(s.curiosity)} disabled={busy} style={{ textAlign: "left", padding: 13 }}>
            {s.emoji} {s.curiosity}
          </button>
        ))}
      </div>
      <Link to="/jugar/cuentos" style={{ textAlign: "center", marginTop: 4 }}>
        {t("spark.myStories")}
      </Link>
    </ScreenCard>
  );
}
