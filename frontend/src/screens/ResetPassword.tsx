import { useState } from "react";
import { Link } from "react-router-dom";
import { resetPassword } from "../api/auth";
import { ApiError } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";
import LanguageSwitcher from "../components/LanguageSwitcher";

export default function ResetPassword() {
  const { t } = useI18n();
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [newCode, setNewCode] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (next.length < 8) { setError(t("validation.passwordShort")); return; }
    if (next !== confirm) { setError(t("pwd.mismatch")); return; }
    setBusy(true);
    try {
      const res = await resetPassword(email.trim(), code.trim(), next);
      setNewCode(res.recovery_code);
    } catch (err) {
      setError(err instanceof ApiError ? t("pwd.resetError") : t("createFamily.error"));
    } finally {
      setBusy(false);
    }
  }

  if (newCode) {
    return (
      <ScreenCard>
        <LanguageSwitcher />
        <h1>{t("pwd.resetTitle")}</h1>
        <p style={{ color: "#0a5a53", fontWeight: 700 }}>{t("pwd.resetDone")}</p>
        <div style={{ background: "#fff", borderRadius: 16, padding: 18, textAlign: "center" }}>
          <code style={{ fontSize: 18, fontWeight: 800, color: "var(--teal-dark)", wordBreak: "break-all" }}>{newCode}</code>
        </div>
        <Link to="/login" style={{ textAlign: "center" }}>{t("pwd.toLogin")}</Link>
      </ScreenCard>
    );
  }

  return (
    <ScreenCard>
      <LanguageSwitcher />
      <h1>{t("pwd.resetTitle")}</h1>
      <p style={{ color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>{t("pwd.resetSubtitle")}</p>
      <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 20, padding: 18 }}>
        <label>{t("field.email")}<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
        <label>{t("pwd.recoveryCode")}<input value={code} onChange={(e) => setCode(e.target.value)} required placeholder="XXXX-XXXX-…" /></label>
        <label>{t("pwd.new")}<input type="password" value={next} onChange={(e) => setNext(e.target.value)} required /></label>
        <label>{t("pwd.confirm")}<input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required /></label>
        {error && <p role="alert" style={{ color: "#c0392b", fontWeight: 700, margin: 0 }}>{error}</p>}
        <Button type="submit" disabled={busy}>{t("pwd.resetSubmit")}</Button>
      </form>
      <Link to="/login" style={{ textAlign: "center", fontSize: 13 }}>{t("pwd.toLogin")}</Link>
    </ScreenCard>
  );
}
