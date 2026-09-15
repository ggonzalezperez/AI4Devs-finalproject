import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createChild } from "../api/children";
import { ApiError } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import { Avatar, AVATAR_IDS, DEFAULT_AVATAR, avatarLabel, type AvatarId } from "../components/avatars";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

function ageFrom(birthdate: string): number | null {
  if (!birthdate) return null;
  const b = new Date(birthdate);
  const t = new Date();
  let age = t.getFullYear() - b.getFullYear();
  const m = t.getMonth() - b.getMonth();
  if (m < 0 || (m === 0 && t.getDate() < b.getDate())) age--;
  return age;
}

export default function AddExplorer() {
  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [pin, setPin] = useState("");
  const [pinConfirm, setPinConfirm] = useState("");
  const [avatar, setAvatar] = useState<AvatarId>(DEFAULT_AVATAR);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const { t } = useI18n();
  const age = ageFrom(birthdate);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!/^\d{4}$/.test(pin)) {
      setError(t("validation.pinLength"));
      return;
    }
    if (pin !== pinConfirm) {
      setError(t("validation.pinMismatch"));
      return;
    }
    setBusy(true);
    try {
      await createChild(name, birthdate, pin, avatar);
      navigate("/familia/explorar");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("addExplorer.error"));
    } finally {
      setBusy(false);
    }
  }

  const pinInputStyle = { letterSpacing: "0.5em", textAlign: "center" as const };

  return (
    <ScreenCard>
      <div>
        <h1>{t("addExplorer.title")}</h1>
        <p style={{ margin: "4px 0 0", color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>
          {t("addExplorer.subtitle")}
        </p>
      </div>
      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 20, padding: 18 }}
      >
        <label>
          {t("field.alias")}
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          {t("field.birthdate")}
          <input
            type="date"
            value={birthdate}
            onChange={(e) => setBirthdate(e.target.value)}
          />
        </label>
        {age !== null && (
          <div
            aria-label="edad calculada"
            style={{ alignSelf: "flex-start", background: "#e6f7ee", color: "#2aa06a", fontWeight: 800, padding: "6px 12px", borderRadius: 12 }}
          >
            {age} {t("common.yearsOld")}
          </div>
        )}
        <div>
          <span style={{ display: "block", fontSize: 13, fontWeight: 800, letterSpacing: "0.02em", color: "var(--teal-dark)", marginBottom: 6 }}>
            {t("addExplorer.avatar")}
          </span>
          <div role="radiogroup" aria-label={t("addExplorer.avatar")} style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 }}>
            {AVATAR_IDS.map((id) => (
              <button
                type="button"
                key={id}
                role="radio"
                aria-checked={avatar === id}
                aria-label={avatarLabel(id)}
                onClick={() => setAvatar(id)}
                style={{
                  padding: 3,
                  minHeight: 0,
                  borderRadius: 14,
                  background: avatar === id ? "rgba(255,122,89,.16)" : "transparent",
                  outline: avatar === id ? "2px solid var(--coral)" : "2px solid transparent",
                  boxShadow: "none",
                }}
              >
                <Avatar id={id} size={44} />
              </button>
            ))}
          </div>
        </div>
        <label>
          {t("field.pin")}
          <input
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={4}
            value={pin}
            onChange={(e) => setPin(e.target.value.replace(/\D/g, ""))}
            style={pinInputStyle}
            required
          />
        </label>
        <small style={{ color: "#0a5a53", fontWeight: 600 }}>{t("addExplorer.pinHint")}</small>
        <label>
          {t("field.pinConfirm")}
          <input
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={4}
            value={pinConfirm}
            onChange={(e) => setPinConfirm(e.target.value.replace(/\D/g, ""))}
            style={pinInputStyle}
            required
          />
        </label>
        {error && (
          <p role="alert" style={{ color: "#c0392b", margin: 0, fontWeight: 700, fontSize: 14 }}>
            {error}
          </p>
        )}
        <Button type="submit" disabled={busy}>
          {t("addExplorer.submit")}
        </Button>
      </form>
    </ScreenCard>
  );
}
