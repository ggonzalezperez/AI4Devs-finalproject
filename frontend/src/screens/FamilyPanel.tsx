import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getChildKnowledge,
  getChildProfile,
  listChildren,
  type Child,
} from "../api/children";
import type { ChildProfile, KnowledgeNode } from "../api/nucleo";
import { useI18n } from "../i18n/I18nContext";
import { Avatar } from "../components/avatars";
import ScreenCard from "../components/ScreenCard";

/**
 * Panel de familia (US5/US6). El adulto ve la ficha de conocimiento de cada
 * hijo: qué domina y qué está descubriendo.
 *
 * El corte fuerte/emergente no es arbitrario. Una isla nace con `mastery = 1`
 * al encender la chispa y solo sube cuando el niño ACIERTA el reto, así que
 * `mastery >= 2` significa "lo exploró y además demostró que lo recuerda".
 */
const MAESTRIA_DOMINADA = 2;

export default function FamilyPanel() {
  const [children, setChildren] = useState<Child[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [profile, setProfile] = useState<ChildProfile | null>(null);
  const [nodes, setNodes] = useState<KnowledgeNode[]>([]);
  const [error, setError] = useState("");
  const { t } = useI18n();

  useEffect(() => {
    listChildren()
      .then((cs) => {
        setChildren(cs);
        if (cs.length > 0) setSelectedId(cs[0].id);
      })
      .catch(() => setError(t("panel.error")));
  }, [t]);

  useEffect(() => {
    if (selectedId === null) return;
    // Se recargan AMBAS al cambiar de hijo: dejar en pantalla datos del hermano
    // anterior sería mezclar información entre hijos.
    setProfile(null);
    setNodes([]);
    setError("");
    Promise.all([getChildProfile(selectedId), getChildKnowledge(selectedId)])
      .then(([p, ns]) => {
        setProfile(p);
        setNodes(ns);
      })
      .catch(() => setError(t("panel.error")));
  }, [selectedId, t]);

  const fuertes = nodes.filter((n) => n.mastery >= MAESTRIA_DOMINADA);
  const emergentes = nodes.filter((n) => n.mastery < MAESTRIA_DOMINADA);

  return (
    <ScreenCard>
      <Link to="/familia/explorar">←</Link>
      <div>
        <h1>{t("panel.title")}</h1>
        <p style={{ margin: "4px 0 0", color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>
          {t("panel.subtitle")}
        </p>
      </div>

      {error && <p role="alert">{error}</p>}

      {children.length > 1 && (
        <>
          <p style={{ margin: 0, fontWeight: 700, color: "var(--teal-dark)" }}>{t("panel.pick")}</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            {children.map((c) => (
              <button
                key={c.id}
                onClick={() => setSelectedId(c.id)}
                aria-pressed={c.id === selectedId}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "8px 14px",
                  border: c.id === selectedId ? "3px solid var(--coral)" : "3px solid transparent",
                }}
              >
                <Avatar id={c.avatar} imageUrl={c.avatar_image_url} size={28} />
                <span>{c.name}</span>
              </button>
            ))}
          </div>
        </>
      )}

      {profile && (
        <div style={{ background: "#fff", borderRadius: 16, padding: "14px 16px", display: "flex", alignItems: "center", gap: 14 }}>
          <Avatar id={profile.avatar} imageUrl={profile.avatar_image_url} size={52} />
          <div>
            <strong style={{ display: "block", fontSize: 20, color: "var(--teal-dark)" }}>{profile.name}</strong>
            <span style={{ fontSize: 13, color: "#0a5a53" }}>
              {profile.age} {t("common.yearsOld")} · 🏝️ {profile.islands} {t("panel.islandsCount")}
            </span>
          </div>
        </div>
      )}

      {profile && nodes.length === 0 && <p style={{ color: "#0a5a53" }}>{t("panel.emptyChild")}</p>}

      {nodes.length > 0 && (
        <>
          <section>
            <h2 style={{ fontSize: 17, margin: "4px 0 2px" }}>⭐ {t("panel.strong")}</h2>
            <p style={{ margin: "0 0 8px", fontSize: 12, color: "#0a5a53" }}>{t("panel.strongHint")}</p>
            <div data-testid="conceptos-fuertes" style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {fuertes.map((n) => (
                <span
                  key={n.id}
                  style={{ background: "#fff", borderRadius: 14, padding: "8px 12px", color: "var(--teal-dark)", fontWeight: 700 }}
                >
                  {n.concept} <span style={{ fontWeight: 400, fontSize: 12 }}>· ⭐ {n.mastery}</span>
                </span>
              ))}
            </div>
          </section>

          <section>
            <h2 style={{ fontSize: 17, margin: "4px 0 2px" }}>🌱 {t("panel.emerging")}</h2>
            <p style={{ margin: "0 0 8px", fontSize: 12, color: "#0a5a53" }}>{t("panel.emergingHint")}</p>
            <div data-testid="conceptos-emergentes" style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {emergentes.map((n) => (
                <span key={n.id} style={{ background: "#fff", borderRadius: 14, padding: "8px 12px", color: "#0a5a53" }}>
                  {n.concept}
                </span>
              ))}
            </div>
          </section>
        </>
      )}
    </ScreenCard>
  );
}
