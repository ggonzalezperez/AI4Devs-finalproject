import { Link, Navigate } from "react-router-dom";
import { useSession } from "../auth/SessionContext";
import { useI18n } from "../i18n/I18nContext";
import ScreenCard from "../components/ScreenCard";
import LanguageSwitcher from "../components/LanguageSwitcher";

export default function Welcome() {
  const { isAuthenticated } = useSession();
  const { t } = useI18n();

  // Si la familia ya tiene sesión, va directa a su espacio (no al registro).
  if (isAuthenticated) return <Navigate to="/familia" replace />;

  return (
    <ScreenCard>
      <LanguageSwitcher />

      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
          gap: 4,
        }}
      >
        <span style={{ fontSize: 12, fontWeight: 800, letterSpacing: "0.14em", textTransform: "uppercase", color: "rgba(255,255,255,.85)" }}>
          {t("welcome.eyebrow")}
        </span>
        <div style={{ fontSize: 64, lineHeight: 1 }} aria-hidden="true">✨</div>
        <h1 className="brand-mark" style={{ fontSize: 46, margin: 0, color: "#fff" }}>
          Chispa
        </h1>
        <p style={{ margin: "8px 4px 0", fontSize: 17, fontWeight: 700, color: "rgba(255,255,255,.92)", lineHeight: 1.35, maxWidth: 320 }}>
          {t("welcome.tagline")}
        </p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <Link to="/crear" className="btn-primary">
          {t("welcome.create")}
        </Link>
        <Link to="/login" className="btn-secondary">
          {t("welcome.login")}
        </Link>
      </div>

      <div
        style={{
          marginTop: 6,
          display: "flex",
          gap: 8,
          alignItems: "center",
          justifyContent: "center",
          background: "rgba(255,255,255,.55)",
          borderRadius: 12,
          padding: "10px 12px",
          fontSize: 12,
          color: "#0a5a53",
        }}
      >
        🔒 {t("createFamily.safety")}
      </div>
    </ScreenCard>
  );
}
