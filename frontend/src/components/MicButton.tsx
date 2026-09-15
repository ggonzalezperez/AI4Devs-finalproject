import { useRef, useState } from "react";
import { useI18n } from "../i18n/I18nContext";

type RecognitionLike = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onend: (() => void) | null;
  onerror: ((e: { error?: string }) => void) | null;
  start: () => void;
  stop: () => void;
};

type RecognitionCtor = new () => RecognitionLike;

function getRecognitionCtor(): RecognitionCtor | null {
  const w = window as unknown as {
    SpeechRecognition?: RecognitionCtor;
    webkitSpeechRecognition?: RecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

/**
 * Códigos de la Web Speech API. Antes se descartaba el error entero, así que
 * "el micrófono no funciona" no traía ninguna pista: el botón parpadeaba y
 * volvía a su sitio. La causa más común, con diferencia, es el permiso.
 */
const MENSAJE_POR_ERROR: Record<string, string> = {
  "not-allowed": "mic.denied",
  "service-not-allowed": "mic.denied",
  "audio-capture": "mic.noMic",
  network: "mic.network",
  "no-speech": "mic.noSpeech",
};

export default function MicButton({
  onText,
  disabled,
}: {
  onText: (text: string) => void;
  disabled?: boolean;
}) {
  const { t, lang } = useI18n();
  const [listening, setListening] = useState(false);
  const [error, setError] = useState("");
  const recRef = useRef<RecognitionLike | null>(null);

  const Ctor = getRecognitionCtor();
  if (!Ctor) return null; // navegador sin soporte → no mostramos el botón

  function toggle() {
    if (listening) {
      recRef.current?.stop();
      return;
    }
    setError("");
    const rec = new Ctor!();
    rec.lang = lang === "en" ? "en-US" : "es-ES";
    rec.continuous = false;
    rec.interimResults = false;
    rec.onresult = (e) => {
      const text = e.results?.[0]?.[0]?.transcript ?? "";
      if (text) onText(text);
    };
    rec.onend = () => setListening(false);
    rec.onerror = (e) => {
      setListening(false);
      setError(t(MENSAJE_POR_ERROR[e?.error ?? ""] ?? "mic.failed"));
    };
    recRef.current = rec;
    setListening(true);
    rec.start();
  }

  return (
    <>
      <button
        type="button"
        onClick={toggle}
        disabled={disabled}
        aria-label={t("voice.dictate")}
        aria-pressed={listening}
        className={listening ? "anim-pulse" : undefined}
        title={listening ? t("mic.listening") : undefined}
        style={{
          width: "auto",
          padding: "0 14px",
          minHeight: 0,
          background: listening ? "var(--coral)" : "#fff",
        }}
      >
        {listening ? "🔴" : "🎤"}
      </button>
      {error && (
        <p
          role="alert"
          style={{ flexBasis: "100%", margin: "6px 0 0", fontSize: 13, color: "var(--teal-dark)", fontWeight: 600 }}
        >
          {error}
        </p>
      )}
    </>
  );
}
