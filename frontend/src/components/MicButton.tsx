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
  onAutoSubmit,
  disabled,
}: {
  onText: (text: string) => void;
  /**
   * Si viene, la pregunta se envía sola al terminar el dictado: el niño habla y
   * Chispa responde, sin el segundo paso de buscar el botón de enviar. Recibe el
   * texto por parámetro a propósito — el estado de React aún no se ha actualizado
   * cuando esto corre, así que leerlo daría la transcripción anterior.
   */
  onAutoSubmit?: (text: string) => void;
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
    // La Web Speech API solo vive en contexto seguro. Servida por IP de la red
    // local (http://192.168.x.x) el navegador rechaza sin llegar a preguntar,
    // y el error que llega es "not-allowed": pedirle permiso al usuario era
    // mandarle a un botón que nadie le va a enseñar.
    if (window.isSecureContext === false) {
      setError(t("mic.insecure"));
      return;
    }
    const rec = new Ctor!();
    rec.lang = lang === "en" ? "en-US" : "es-ES";
    rec.continuous = false;
    rec.interimResults = false;
    rec.onresult = (e) => {
      const text = e.results?.[0]?.[0]?.transcript ?? "";
      if (!text) return;
      onText(text);
      onAutoSubmit?.(text);
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
