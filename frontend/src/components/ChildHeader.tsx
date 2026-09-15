import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getProfile, type ChildProfile } from "../api/nucleo";
import { useI18n } from "../i18n/I18nContext";
import { Avatar } from "./avatars";

export default function ChildHeader() {
  const [p, setP] = useState<ChildProfile | null>(null);
  const { t } = useI18n();

  useEffect(() => {
    getProfile()
      .then(setP)
      .catch(() => undefined);
  }, []);

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, marginBottom: 6 }}>
      <Link to="/jugar" aria-label={t("child.home")} style={{ fontSize: 22, textDecoration: "none" }}>
        🏠
      </Link>
      {p?.name && (
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Avatar id={p.avatar} imageUrl={p.avatar_image_url} size={30} />
          <div style={{ fontFamily: "var(--font-head)", fontWeight: 600, color: "var(--teal-dark)" }}>
            {t("child.hi")} {p.name}
          </div>
        </div>
      )}
      <Link
        to="/jugar/mis-islas"
        style={{ background: "#fff", borderRadius: 999, padding: "4px 12px", fontWeight: 800, color: "var(--coral)", textDecoration: "none", fontSize: 14 }}
      >
        🏝️ {p?.islands ?? 0}
      </Link>
      {/* Salida hacia la zona de familia. Deliberadamente discreta: un niño no
          debe sentirse invitado a pulsarla, y detrás pide la contraseña. */}
      <Link
        to="/jugar/salir"
        style={{ fontSize: 12, color: "#0a5a53", opacity: 0.75, textDecoration: "none" }}
      >
        {t("exit.link")}
      </Link>
    </div>
  );
}
