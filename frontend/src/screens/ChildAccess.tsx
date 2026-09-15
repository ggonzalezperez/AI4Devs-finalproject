import { useEffect, useState } from "react";
import { Link, useNavigate, useParams, useLocation } from "react-router-dom";
import { childLogin } from "../api/children";
import { setChildToken } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import { Avatar } from "../components/avatars";
import ScreenCard from "../components/ScreenCard";

export default function ChildAccess() {
  const { childId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const avatar = (location.state as { avatar?: string } | null)?.avatar;
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const { t } = useI18n();

  useEffect(() => {
    if (pin.length === 4 && childId) {
      childLogin(Number(childId), pin)
        .then((res) => {
          setChildToken(res.access_token);
          navigate("/jugar");
        })
        .catch(() => {
          setError(t("childAccess.error"));
          setPin("");
        });
    }
  }, [pin, childId, t, navigate]);

  const keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "⌫"];

  return (
    <ScreenCard>
      <div style={{ textAlign: "center" }}>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <Avatar id={avatar} size={72} />
        </div>
        <div style={{ color: "#0a5a53", fontWeight: 600, marginTop: 2 }}>{t("childAccess.title")}</div>
      </div>
      <div aria-label="pin" style={{ display: "flex", gap: 14, justifyContent: "center", marginTop: 6 }}>
        {[0, 1, 2, 3].map((i) => (
          <span
            key={i}
            style={{
              width: 16,
              height: 16,
              borderRadius: 99,
              background: i < pin.length ? "var(--coral)" : "rgba(255,255,255,.5)",
            }}
          />
        ))}
      </div>
      {error && <p role="alert" style={{ textAlign: "center", color: "#fff", fontWeight: 700 }}>{error}</p>}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 14, marginTop: 14 }}>
        {keys.map((k, idx) =>
          k === "" ? (
            <div key={idx} />
          ) : (
            <button
              key={idx}
              onClick={() =>
                k === "⌫" ? setPin((p) => p.slice(0, -1)) : setPin((p) => (p + k).slice(0, 4))
              }
            >
              {k}
            </button>
          ),
        )}
      </div>
      <Link to="/familia/explorar" style={{ textAlign: "center", fontSize: 13, marginTop: 10 }}>
        {t("landing.familySettings")}
      </Link>
    </ScreenCard>
  );
}
