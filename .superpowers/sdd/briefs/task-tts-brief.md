# Task TTS: Leer la lección en voz alta (Web Speech Synthesis)

Frontend `frontend/`. Rama `feature-fasec-extra`. SIN push.
Botón "🔊 Escuchar" en cada turno del chat que lee la lección en voz alta con la API nativa del navegador (`speechSynthesis`). Multiidioma (idioma activo de la app), ligero, sin modelo ni servidor. Si el navegador no la soporta, el botón no se muestra. Ideal para niños que aún no leen.

**Files:**
- Create: `frontend/src/components/SpeakButton.tsx`
- Modify: `frontend/src/screens/LessonScreen.tsx` (botón en cada turno)
- Modify: `frontend/src/i18n/translations.ts` (`voice.listen`)
- Test: `frontend/src/components/SpeakButton.test.tsx`

## Step 1: `frontend/src/components/SpeakButton.tsx`
```tsx
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
```

## Step 2: i18n — `frontend/src/i18n/translations.ts`
es: `"voice.listen": "Escuchar la lección",`
en: `"voice.listen": "Listen to the lesson",`

## Step 3: `frontend/src/screens/LessonScreen.tsx`
- Importa `import SpeakButton from "../components/SpeakButton";`
- Dentro de `ChatTurn`, en la burbuja de Chispa, junto al título (`{turn.title}`), pon el botón a su lado. Sustituye el `<div ...>{turn.title}</div>` por una fila con el título y el botón:
```tsx
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ fontWeight: 700, fontSize: 16, flex: 1 }}>{turn.title}</div>
          <SpeakButton text={`${turn.title}. ${turn.body} ${turn.fun_fact}`} />
        </div>
```
(Si el título se renderiza distinto en tu versión, localiza el `{turn.title}` dentro del bloque de la respuesta de Chispa y colócale el `SpeakButton` al lado, leyendo título + cuerpo + dato.)

## Step 4: Test `frontend/src/components/SpeakButton.test.tsx`
```tsx
import { render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import SpeakButton from "./SpeakButton";

afterEach(() => vi.unstubAllGlobals());

test("renders nothing when speech synthesis is unsupported", () => {
  // jsdom no define speechSynthesis
  const { container } = render(
    <I18nProvider initialLang="es">
      <SpeakButton text="hola" />
    </I18nProvider>,
  );
  expect(container.querySelector("button")).toBeNull();
});

test("shows the listen button when supported", () => {
  vi.stubGlobal("speechSynthesis", { speak: () => {}, cancel: () => {}, speaking: false });
  vi.stubGlobal("SpeechSynthesisUtterance", class { lang = ""; rate = 1; onend = null; onerror = null; constructor(public text: string) {} });
  render(
    <I18nProvider initialLang="es">
      <SpeakButton text="hola" />
    </I18nProvider>,
  );
  expect(screen.getByRole("button", { name: /escuchar la lección/i })).toBeInTheDocument();
});
```

## Step 5: Verificación
- `npm test` → todo PASS (en jsdom el botón es null en los tests de LessonScreen, sin impacto).
- `npm run lint` → limpio.

## Step 6: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): read-aloud lessons (Web Speech Synthesis, multilingual)"
```
