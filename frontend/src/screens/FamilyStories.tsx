import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getFamilyStories, reviewStory, type Story } from "../api/stories";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

export default function FamilyStories() {
  const [stories, setStories] = useState<Story[]>([]);
  const [error, setError] = useState("");
  const [loaded, setLoaded] = useState(false);
  const { t } = useI18n();

  function load() {
    getFamilyStories()
      .then(setStories)
      .catch(() => setError(t("familyStories.error")))
      .finally(() => setLoaded(true));
  }

  useEffect(load, []);

  const statusLabel: Record<string, string> = {
    pending: t("familyStories.pending"),
    approved: t("familyStories.approved"),
    rejected: t("familyStories.rejected"),
  };

  return (
    <ScreenCard>
      <div>
        <h1>{t("familyStories.title")}</h1>
        <p style={{ margin: "4px 0 0", color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>
          {t("familyStories.subtitle")}
        </p>
      </div>
      {error && <p role="alert">{error}</p>}
      {loaded && stories.length === 0 && !error && (
        <p style={{ color: "#0a5a53", fontWeight: 600 }}>{t("familyStories.empty")}</p>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {stories.map((s) => (
          <StoryRow key={s.id} story={s} statusLabel={statusLabel} onReviewed={load} />
        ))}
      </div>
      <Link to="/familia/explorar" style={{ textAlign: "center", marginTop: 8 }}>
        ←
      </Link>
    </ScreenCard>
  );
}

function StoryRow({
  story,
  statusLabel,
  onReviewed,
}: {
  story: Story;
  statusLabel: Record<string, string>;
  onReviewed: () => void;
}) {
  const [title, setTitle] = useState(story.title);
  const [body, setBody] = useState(story.body);
  const [busy, setBusy] = useState(false);
  const { t } = useI18n();
  const pending = story.status === "pending";

  async function review(action: "approve" | "reject") {
    setBusy(true);
    try {
      // Al aprobar guardamos las posibles ediciones; al rechazar no tocamos el texto.
      if (action === "approve") {
        await reviewStory(story.id, action, title, body);
      } else {
        await reviewStory(story.id, action);
      }
      onReviewed();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ background: "#fff", borderRadius: 16, padding: 16, display: "flex", flexDirection: "column", gap: 8 }}>
      <span style={{ fontSize: 12, fontWeight: 800, color: "var(--coral)" }}>
        {statusLabel[story.status] ?? story.status}
      </span>
      {pending ? (
        <>
          <label style={{ fontSize: 12, fontWeight: 700, color: "#0a5a53" }}>
            {t("familyStories.titleLabel")}
          </label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} aria-label={t("familyStories.titleLabel")} />
          <label style={{ fontSize: 12, fontWeight: 700, color: "#0a5a53" }}>
            {t("familyStories.bodyLabel")}
          </label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            rows={5}
            aria-label={t("familyStories.bodyLabel")}
            style={{ fontFamily: "inherit", fontSize: 14, lineHeight: 1.5 }}
          />
          <div style={{ display: "flex", gap: 8 }}>
            <Button onClick={() => void review("approve")} disabled={busy}>
              {t("familyStories.approve")}
            </Button>
            <button onClick={() => void review("reject")} disabled={busy} style={{ padding: "10px 14px" }}>
              {t("familyStories.reject")}
            </button>
          </div>
        </>
      ) : (
        <>
          <strong style={{ color: "var(--teal-dark)" }}>{story.title}</strong>
          <p style={{ color: "#0a5a53", margin: 0, lineHeight: 1.5 }}>{story.body}</p>
        </>
      )}
    </div>
  );
}
