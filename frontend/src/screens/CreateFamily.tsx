import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { registerFamily } from "../api/auth";
import { ApiError } from "../api/client";
import { useSession } from "../auth/SessionContext";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";
import LanguageSwitcher from "../components/LanguageSwitcher";

export default function CreateFamily() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [pending, setPending] = useState<{ token: string; code: string } | null>(null);
  const { isAuthenticated, login } = useSession();
  const { t } = useI18n();
  const navigate = useNavigate();

  if (isAuthenticated) return <Navigate to="/familia" replace />;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (password.length < 8) {
      setError(t("validation.passwordShort"));
      return;
    }
    if (password !== confirm) {
      setError(t("validation.passwordMismatch"));
      return;
    }
    setBusy(true);
    try {
      const { access_token, recovery_code } = await registerFamily(name, email, password);
      setPending({ token: access_token, code: recovery_code });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("createFamily.error"));
    } finally {
      setBusy(false);
    }
  }

  if (pending) {
    return (
      <ScreenCard>
        <LanguageSwitcher />
        <h1>{t("pwd.recoveryTitle")}</h1>
        <p style={{ color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>{t("pwd.recoverySubtitle")}</p>
        <div style={{ background: "#fff", borderRadius: 16, padding: 18, textAlign: "center" }}>
          <code style={{ fontSize: 18, fontWeight: 800, color: "var(--teal-dark)", wordBreak: "break-all" }}>
            {pending.code}
          </code>
        </div>
        <button onClick={() => { void navigator.clipboard?.writeText(pending.code); }}>{t("pwd.copy")}</button>
        <Button onClick={() => { login(pending.token); navigate("/familia"); }}>{t("pwd.continue")}</Button>
      </ScreenCard>
    );
  }

  return (
    <ScreenCard>
      <LanguageSwitcher />
      <div>
        <h1>{t("createFamily.title")}</h1>
        <p style={{ margin: "4px 0 0", color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>
          {t("createFamily.subtitle")}
        </p>
      </div>
      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 20, padding: 18 }}
      >
        <label>
          {t("field.name")}
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
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
        <label>
          {t("field.passwordConfirm")}
          <input
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
          />
        </label>
        {error && (
          <p role="alert" style={{ color: "#c0392b", margin: 0, fontWeight: 700, fontSize: 14 }}>
            {error}
          </p>
        )}
        <Button type="submit" disabled={busy}>
          {t("createFamily.submit")}
        </Button>
      </form>
      <p style={{ textAlign: "center", fontSize: 13 }}>
        {t("createFamily.haveAccount")} <Link to="/login">{t("action.enter")}</Link>
      </p>
      <div
        style={{ marginTop: "auto", display: "flex", gap: 8, alignItems: "center", background: "rgba(255,255,255,.55)", borderRadius: 12, padding: "10px 12px", fontSize: 12, color: "#0a5a53" }}
      >
        🔒 {t("createFamily.safety")}
      </div>
    </ScreenCard>
  );
}
