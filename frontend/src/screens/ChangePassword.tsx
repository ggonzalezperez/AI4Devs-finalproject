import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { changePassword } from "../api/auth";
import { ApiError } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

export default function ChangePassword() {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (next.length < 8) { setError(t("validation.passwordShort")); return; }
    if (next !== confirm) { setError(t("pwd.mismatch")); return; }
    setBusy(true);
    try {
      await changePassword(current, next);
      setDone(true);
    } catch (err) {
      setError(err instanceof ApiError && err.status === 400 ? t("pwd.currentWrong") : t("createFamily.error"));
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    if (!done) return;
    const id = setTimeout(() => navigate("/familia"), 1200);
    return () => clearTimeout(id);
  }, [done, navigate]);

  return (
    <ScreenCard>
      <Link to="/familia/explorar">←</Link>
      <h1>{t("pwd.changeTitle")}</h1>
      <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 20, padding: 18 }}>
        <label>{t("pwd.current")}<input type="password" value={current} onChange={(e) => setCurrent(e.target.value)} required /></label>
        <label>{t("pwd.new")}<input type="password" value={next} onChange={(e) => setNext(e.target.value)} required /></label>
        <label>{t("pwd.confirm")}<input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required /></label>
        {error && <p role="alert" style={{ color: "#c0392b", fontWeight: 700, margin: 0 }}>{error}</p>}
        {done && <p style={{ color: "var(--green)", fontWeight: 700, margin: 0 }}>{t("pwd.changed")}</p>}
        <Button type="submit" disabled={busy}>{t("pwd.save")}</Button>
      </form>
    </ScreenCard>
  );
}
