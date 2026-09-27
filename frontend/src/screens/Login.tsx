import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { loginFamily } from "../api/auth";
import { ApiError } from "../api/client";
import { useSession } from "../auth/SessionContext";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";
import LanguageSwitcher from "../components/LanguageSwitcher";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { isAuthenticated, login } = useSession();
  const { t } = useI18n();
  const navigate = useNavigate();

  if (isAuthenticated) return <Navigate to="/familia" replace />;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { access_token } = await loginFamily(email, password);
      login(access_token);
      navigate("/familia");
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) setError(t("error.tooManyAttempts"));
      else setError(err instanceof ApiError ? t("login.error") : t("login.errorGeneric"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <LanguageSwitcher />
      <h1>{t("login.title")}</h1>
      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 20, padding: 18 }}
      >
        <label>
          {t("field.email")}
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          {t("field.password")}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && (
          <p role="alert" style={{ color: "#c0392b", margin: 0, fontWeight: 700, fontSize: 14 }}>
            {error}
          </p>
        )}
        <Button type="submit" disabled={busy}>
          {t("action.enter")}
        </Button>
      </form>
      <p style={{ textAlign: "center", fontSize: 13 }}>
        {t("login.new")} <Link to="/crear">{t("createFamily.submit")}</Link>
      </p>
      <p style={{ textAlign: "center", fontSize: 13 }}>
        <Link to="/recuperar">{t("pwd.forgot")}</Link>
      </p>
    </ScreenCard>
  );
}
