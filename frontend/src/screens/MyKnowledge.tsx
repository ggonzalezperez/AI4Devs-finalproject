import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getKnowledge, type KnowledgeNode } from "../api/nucleo";
import { useI18n } from "../i18n/I18nContext";
import ScreenCard from "../components/ScreenCard";
import ChildHeader from "../components/ChildHeader";

export default function MyKnowledge() {
  const [nodes, setNodes] = useState<KnowledgeNode[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [query, setQuery] = useState("");
  const { t } = useI18n();

  useEffect(() => {
    getKnowledge()
      .then(setNodes)
      .catch(() => undefined)
      .finally(() => setLoaded(true));
  }, []);

  const norm = (s: string) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  const filtered = query.trim()
    ? nodes.filter((n) => norm(n.concept).includes(norm(query)) || norm(n.subject).includes(norm(query)))
    : nodes;

  return (
    <ScreenCard>
      <ChildHeader />
      <h1>{t("islands.title")}</h1>
      {loaded && nodes.length === 0 && <p style={{ color: "#0a5a53" }}>{t("islands.empty")}</p>}
      {loaded && nodes.length > 0 && (
        <p style={{ margin: 0, color: "#0a5a53", fontWeight: 600, fontSize: 13 }}>{t("islands.tapHint")}</p>
      )}
      {loaded && nodes.length > 0 && (
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t("islands.search")}
          aria-label={t("islands.search")}
        />
      )}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
        {filtered.map((n) => {
          const card = (
            <div style={{ background: "#fff", borderRadius: 16, padding: "12px 14px", minWidth: 120 }}>
              <div style={{ fontSize: 26 }}>🏝️</div>
              <strong style={{ color: "var(--teal-dark)" }}>{n.concept}</strong>
              <div style={{ fontSize: 12, color: "#0a5a53" }}>
                {n.subject} · ⭐ {n.mastery}
              </div>
            </div>
          );
          return n.root_lesson_id ? (
            <Link key={n.id} to={`/jugar/leccion/${n.root_lesson_id}`} style={{ textDecoration: "none" }}>
              {card}
            </Link>
          ) : (
            <div key={n.id}>{card}</div>
          );
        })}
      </div>
      {loaded && nodes.length > 0 && filtered.length === 0 && (
        <p style={{ color: "#0a5a53" }}>{t("islands.noMatch")}</p>
      )}
      <Link to="/jugar" style={{ textAlign: "center", marginTop: 8 }}>
        {t("islands.more")}
      </Link>
    </ScreenCard>
  );
}
