import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { listChildren, generateChildAvatar, type Child } from "../api/children";
import { ApiError } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import { Avatar } from "../components/avatars";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

export default function ChildAvatar() {
  const { childId } = useParams();
  const id = Number(childId);
  const { t } = useI18n();
  const [child, setChild] = useState<Child | null>(null);
  const [desc, setDesc] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    listChildren().then((cs) => setChild(cs.find((c) => c.id === id) ?? null)).catch(() => undefined);
  }, [id]);

  async function generate() {
    if (!desc.trim()) return;
    setBusy(true);
    setError("");
    try {
      const updated = await generateChildAvatar(id, desc.trim());
      setChild(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("avatarAI.error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <Link to="/familia/explorar">←</Link>
      <h1>{t("avatarAI.title")}</h1>
      <p style={{ color: "#0a5a53", fontWeight: 600, fontSize: 14, margin: 0 }}>{t("avatarAI.subtitle")}</p>
      <div style={{ display: "flex", justifyContent: "center", margin: "8px 0" }}>
        <Avatar id={child?.avatar} imageUrl={child?.avatar_image_url} size={120} />
      </div>
      <input
        value={desc}
        onChange={(e) => setDesc(e.target.value)}
        placeholder={t("avatarAI.placeholder")}
        aria-label={t("avatarAI.placeholder")}
      />
      {error && <p role="alert" style={{ color: "#c0392b", fontWeight: 700, margin: 0 }}>{error}</p>}
      <Button onClick={() => void generate()} disabled={busy}>
        {busy ? t("avatarAI.generating") : t("avatarAI.generate")}
      </Button>
    </ScreenCard>
  );
}
