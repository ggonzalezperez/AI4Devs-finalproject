import { useState } from "react";
import { Link } from "react-router-dom";
import { QRCodeSVG } from "qrcode.react";
import { useI18n } from "../i18n/I18nContext";
import ScreenCard from "../components/ScreenCard";

export default function ConnectDevice() {
  const { t } = useI18n();
  const [copied, setCopied] = useState(false);
  const url = window.location.origin;
  const isLocal = /localhost|127\.0\.0\.1/.test(url);

  async function copy() {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // sin portapapeles: el usuario puede copiar a mano
    }
  }

  return (
    <ScreenCard>
      <div>
        <h1>{t("connect.title")}</h1>
        <p style={{ margin: "4px 0 0", color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>
          {t("connect.subtitle")}
        </p>
      </div>

      <div style={{ background: "#fff", borderRadius: 20, padding: 18, display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
        <QRCodeSVG value={url} size={188} bgColor="#ffffff" fgColor="#08433e" />
        <code style={{ fontWeight: 800, color: "var(--teal-dark)", wordBreak: "break-all", textAlign: "center" }}>
          {url}
        </code>
        <button onClick={() => void copy()} style={{ width: "100%" }}>
          {copied ? t("connect.copied") : t("connect.copy")}
        </button>
      </div>

      {isLocal && (
        <p role="alert" style={{ background: "rgba(255,255,255,.6)", borderRadius: 12, padding: 12, color: "#0a5a53", fontSize: 13, margin: 0 }}>
          ⚠️ {t("connect.localhostWarn")}
        </p>
      )}

      <Link to="/familia/explorar" style={{ textAlign: "center", marginTop: 4 }}>
        ←
      </Link>
    </ScreenCard>
  );
}
