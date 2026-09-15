import { useI18n } from "../i18n/I18nContext";

/**
 * Señal de que la respuesta está en camino.
 *
 * Con el generador de demo la respuesta era instantánea y no hacía falta. Con
 * una IA real son varios segundos, y sin esto el niño ve la pantalla congelada,
 * cree que se ha roto y vuelve a pulsar.
 *
 * Se coloca DONDE va a aparecer la respuesta, para que mire al sitio correcto.
 * `role="status"` lo anuncia a un lector de pantalla sin robar el foco, y las
 * animaciones se apagan solas con `prefers-reduced-motion`.
 */
export default function Thinking() {
  const { t } = useI18n();

  return (
    <div
      role="status"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        background: "#fff",
        borderRadius: 16,
        padding: "12px 16px",
        color: "var(--teal-dark)",
        fontWeight: 700,
      }}
    >
      <span className="anim-pulse" aria-hidden style={{ fontSize: 22, lineHeight: 1 }}>
        ✨
      </span>
      <span>{t("thinking")}</span>
      <span aria-hidden style={{ letterSpacing: 2 }}>
        <span className="anim-dot">.</span>
        <span className="anim-dot">.</span>
        <span className="anim-dot">.</span>
      </span>
    </div>
  );
}
