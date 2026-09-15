import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createStory, getMyStories, type Story } from "../api/stories";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";
import ChildHeader from "../components/ChildHeader";

export default function StoryLibrary() {
  const [stories, setStories] = useState<Story[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [busy, setBusy] = useState(false);
  const [justCreated, setJustCreated] = useState(false);
  const { t } = useI18n();

  function load() {
    getMyStories()
      .then(setStories)
      .catch(() => undefined)
      .finally(() => setLoaded(true));
  }

  useEffect(load, []);

  async function create() {
    setBusy(true);
    setJustCreated(false);
    try {
      await createStory();
      setJustCreated(true);
    } catch {
      // silencioso: el niño no ve errores técnicos
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <ChildHeader />
      <h1>{t("stories.title")}</h1>
      <Button onClick={() => void create()} disabled={busy}>
        {busy ? t("stories.creating") : t("stories.create")}
      </Button>
      {justCreated && (
        <p role="status" style={{ background: "#fff", borderRadius: 16, padding: 12, color: "#0a5a53", fontWeight: 700 }}>
          {t("stories.pending")}
        </p>
      )}
      {loaded && stories.length === 0 && <p style={{ color: "#0a5a53" }}>{t("stories.empty")}</p>}
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {stories.map((s) => (
          <Link
            key={s.id}
            to={`/jugar/cuentos/${s.id}`}
            style={{ background: "#fff", borderRadius: 16, padding: "14px 16px", textDecoration: "none", color: "var(--teal-dark)" }}
          >
            <span style={{ fontSize: 22 }}>📖</span> <strong>{s.title}</strong>
          </Link>
        ))}
      </div>
      <Link to="/jugar" style={{ textAlign: "center", marginTop: 8 }}>
        {t("islands.more")}
      </Link>
    </ScreenCard>
  );
}
