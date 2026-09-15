import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { listChildren, type Child } from "../api/children";
import { useI18n } from "../i18n/I18nContext";
import { Avatar } from "../components/avatars";
import ScreenCard from "../components/ScreenCard";

export default function WhoExplores() {
  const [children, setChildren] = useState<Child[]>([]);
  const [error, setError] = useState("");
  const [loaded, setLoaded] = useState(false);
  const navigate = useNavigate();
  const { t } = useI18n();

  useEffect(() => {
    listChildren()
      .then(setChildren)
      .catch(() => setError(t("who.error")))
      .finally(() => setLoaded(true));
  }, [t]);

  return (
    <ScreenCard>
      <div>
        <h1>{t("who.title")}</h1>
        <p style={{ margin: "4px 0 0", color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>
          {t("who.subtitle")}
        </p>
      </div>
      {error && <p role="alert">{error}</p>}
      {loaded && children.length === 0 && !error && (
        <p style={{ color: "#0a5a53", fontWeight: 600 }}>{t("who.empty")}</p>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {children.map((c) => (
          <button
            key={c.id}
            onClick={() => navigate(`/explorar/${c.id}`, { state: { name: c.name, avatar: c.avatar } })}
            style={{ display: "flex", alignItems: "center", gap: 14, textAlign: "left", padding: 16 }}
          >
            <Avatar id={c.avatar} imageUrl={c.avatar_image_url} size={46} />
            <span style={{ flex: 1 }}>
              <strong style={{ display: "block", fontSize: 18 }}>{c.name}</strong>
              <span style={{ fontSize: 13, color: "#0a5a53" }}>
                {c.age} {t("common.yearsOld")}
              </span>
            </span>
            <Link
              to={`/familia/explorador/${c.id}`}
              onClick={(e) => e.stopPropagation()}
              style={{ fontSize: 18, textDecoration: "none" }}
            >
              ✨
            </Link>
            <span style={{ color: "var(--coral)", fontSize: 22 }}>→</span>
          </button>
        ))}
      </div>
      <Link to="/familia/nuevo" style={{ textAlign: "center", marginTop: 4 }}>
        {t("who.addExplorer")}
      </Link>
      <p style={{ fontSize: 12, color: "#0a5a53", textAlign: "center", margin: "8px 0 0" }}>
        {t("who.demoHint")}
      </p>
      <Link to="/familia/panel" style={{ textAlign: "center", marginTop: 4 }}>
        {t("panel.link")}
      </Link>
      <Link to="/familia/ia" style={{ textAlign: "center", marginTop: 4 }}>
        {t("aiPanel.link")}
      </Link>
      <Link to="/familia/cuentos" style={{ textAlign: "center", marginTop: 4 }}>
        {t("familyStories.link")}
      </Link>
      <Link to="/familia/conectar" style={{ textAlign: "center", marginTop: 4 }}>
        {t("connect.link")}
      </Link>
      <Link to="/familia/password" style={{ textAlign: "center", marginTop: 4 }}>{t("pwd.changeLink")}</Link>
    </ScreenCard>
  );
}
