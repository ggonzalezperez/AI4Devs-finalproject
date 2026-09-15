# Task Voz: Dictar la pregunta con micrófono (Web Speech API)

Frontend `frontend/`. Rama `feature-buscador-voz`. SIN push.
Los niños hablan más que escriben: añade un **botón de micrófono** para dictar la pregunta, usando la API nativa del navegador (`SpeechRecognition`/`webkitSpeechRecognition`). Es **rápido, ligero y multiidioma** (usa el idioma activo de la app). Sin dependencias nuevas ni servidor. Si el navegador no la soporta, el botón **no se muestra** (degradación elegante).

**Files:**
- Create: `frontend/src/components/MicButton.tsx`
- Modify: `frontend/src/screens/Spark.tsx` (micro junto al input de curiosidad)
- Modify: `frontend/src/screens/LessonScreen.tsx` (micro junto al input del chat)
- Modify: `frontend/src/i18n/translations.ts` (`voice.dictate`)
- Test: `frontend/src/components/MicButton.test.tsx`

## Step 1: `frontend/src/components/MicButton.tsx`
```tsx
import { useRef, useState } from "react";
import { useI18n } from "../i18n/I18nContext";

type RecognitionLike = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
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

export default function MicButton({
  onText,
  disabled,
}: {
  onText: (text: string) => void;
  disabled?: boolean;
}) {
  const { t, lang } = useI18n();
  const [listening, setListening] = useState(false);
  const recRef = useRef<RecognitionLike | null>(null);

  const Ctor = getRecognitionCtor();
  if (!Ctor) return null; // navegador sin soporte → no mostramos el botón

  function toggle() {
    if (listening) {
      recRef.current?.stop();
      return;
    }
    const rec = new Ctor!();
    rec.lang = lang === "en" ? "en-US" : "es-ES";
    rec.continuous = false;
    rec.interimResults = false;
    rec.onresult = (e) => {
      const text = e.results?.[0]?.[0]?.transcript ?? "";
      if (text) onText(text);
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    recRef.current = rec;
    setListening(true);
    rec.start();
  }

  return (
    <button
      type="button"
      onClick={toggle}
      disabled={disabled}
      aria-label={t("voice.dictate")}
      aria-pressed={listening}
      style={{ width: "auto", padding: "0 14px", minHeight: 0, background: listening ? "var(--coral)" : "#fff" }}
    >
      {listening ? "🔴" : "🎤"}
    </button>
  );
}
```
Nota: `useI18n` debe exponer `lang`. Si NO lo expone, usa el idioma del documento como respaldo: sustituye `const { t, lang } = useI18n();` por `const { t } = useI18n();` y `rec.lang = (document.documentElement.lang || navigator.language || "es").startsWith("en") ? "en-US" : "es-ES";`. Comprueba primero `I18nContext` para ver si `lang` está disponible y elige la variante que compile.

## Step 2: i18n — `frontend/src/i18n/translations.ts`
es: `"voice.dictate": "Dictar la pregunta",`
en: `"voice.dictate": "Dictate the question",`

## Step 3: `frontend/src/screens/Spark.tsx`
- Importa `import MicButton from "../components/MicButton";`
- Envuelve el `<input>` de la curiosidad y el micro en una fila. Sustituye el bloque del `<input ... aria-label={t("spark.placeholder")} />` por:
```tsx
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={curiosity}
            onChange={(e) => setCuriosity(e.target.value)}
            placeholder={t("spark.placeholder")}
            aria-label={t("spark.placeholder")}
            style={{ flex: 1 }}
          />
          <MicButton onText={setCuriosity} disabled={busy} />
        </div>
```
(Mantén el resto del formulario igual.)

## Step 4: `frontend/src/screens/LessonScreen.tsx`
- Importa `import MicButton from "../components/MicButton";`
- En el `<form>` del chat (input + botón 🔎), añade el micro entre el input y el submit:
```tsx
            <MicButton onText={setQuestion} disabled={busy} />
```
(colócalo justo después del `</input>`/`<input .../>` y antes del `<button type="submit" ...>🔎</button>`.)

## Step 5: Test `frontend/src/components/MicButton.test.tsx`
En jsdom no hay `SpeechRecognition`, así que el botón no se renderiza. Verifica la degradación y el caso soportado con un stub:
```tsx
import { render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import MicButton from "./MicButton";

afterEach(() => {
  vi.unstubAllGlobals();
});

test("renders nothing when speech recognition is unsupported", () => {
  const { container } = render(
    <I18nProvider initialLang="es">
      <MicButton onText={() => {}} />
    </I18nProvider>,
  );
  expect(container.querySelector("button")).toBeNull();
});

test("shows the mic button when supported", () => {
  class FakeRec {
    lang = "";
    continuous = false;
    interimResults = false;
    onresult = null;
    onend = null;
    onerror = null;
    start() {}
    stop() {}
  }
  vi.stubGlobal("SpeechRecognition", FakeRec);
  render(
    <I18nProvider initialLang="es">
      <MicButton onText={() => {}} />
    </I18nProvider>,
  );
  expect(screen.getByRole("button", { name: /dictar la pregunta/i })).toBeInTheDocument();
});
```

## Step 6: Verificación
- `npm test` → todo PASS (Spark y LessonScreen siguen verdes: en jsdom MicButton es null, sin impacto).
- `npm run lint` → limpio.

## Step 7: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): voice dictation for questions (Web Speech API, multilingual)"
```
