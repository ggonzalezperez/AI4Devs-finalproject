import { useEffect, useState } from "react";
import { useI18n } from "../i18n/I18nContext";

export default function SpeakButton({ text, disabled }: { text: string; disabled?: boolean }) {
  const { t, lang } = useI18n();
  const [speaking, setSpeaking] = useState(false);

  const synth = typeof window !== "undefined" ? window.speechSynthesis : undefined;

  // Si se desmonta mientras habla, detén la locución.
  useEffect(() => {
    return () => {
      if (synth && synth.speaking) synth.cancel();
    };
  }, [synth]);

  if (!synth || typeof SpeechSynthesisUtterance === "undefined") return null;

  function toggle() {
    if (speaking) {
      synth!.cancel();
      setSpeaking(false);
      return;
    }
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang === "en" ? "en-US" : "es-ES";
    u.rate = 0.95;
    u.onend = () => setSpeaking(false);
    u.onerror = () => setSpeaking(false);
    setSpeaking(true);
    synth!.cancel(); // corta cualquier locución previa
    synth!.speak(u);
  }

  return (
    <button
      type="button"
      onClick={toggle}
      disabled={disabled}
      aria-label={t("voice.listen")}
      aria-pressed={speaking}
      style={{ width: "auto", padding: "4px 10px", minHeight: 0, fontSize: 14 }}
    >
      {speaking ? "⏹️" : "🔊"}
    </button>
  );
}
