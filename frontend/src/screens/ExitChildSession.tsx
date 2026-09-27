import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { verifyFamilyPassword } from "../api/auth";
import { ApiError, setChildToken } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

/**
 * Salir de la sesión del niño (US5/US6, «padres con control, niño con agencia»).
 *
 * El token de familia sigue en el dispositivo mientras el niño juega, así que
 * tenerlo no demuestra nada: quien pulsa podría ser el niño. Por eso se pide la
 * contraseña otra vez antes de devolver el mando al adulto.
 */
export default function ExitChildSession() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const { t } = useI18n();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await verifyFamilyPassword(password);
      // Solo se cierra la sesión del NIÑO; la de familia sigue viva.
      setChildToken(null);
      navigate("/familia/explorar", { replace: true });
    } catch (err) {
      const esperar = err instanceof ApiError && err.status === 429;
      setError(t(esperar ? "error.tooManyAttempts" : "exit.wrong"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <h1>{t("exit.title")}</h1>
      <p style={{ color: "#0a5a53", fontWeight: 600, fontSize: 14, margin: "4px 0 0" }}>
        {t("exit.subtitle")}
      </p>

      <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <label>
          {t("exit.password")}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {error && <p role="alert">{error}</p>}
        <Button type="submit" disabled={busy}>
          {t("exit.submit")}
        </Button>
      </form>

      <Link to="/jugar" style={{ textAlign: "center", marginTop: 8 }}>
        {t("exit.back")}
      </Link>
    </ScreenCard>
  );
}
