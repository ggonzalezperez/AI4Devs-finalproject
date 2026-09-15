# Task B2: Pantalla "Encender la chispa" (Spark)

Usa el código EXACTO. Frontend `frontend/`. Rama `feature-entrega3-nucleo`. SIN push.

**Files:**
- Create: `frontend/src/screens/Spark.tsx`
- Modify: `frontend/src/i18n/translations.ts` (añadir claves a es y en)
- Test: `frontend/src/screens/Spark.test.tsx`

## Step 1: Añadir claves i18n en `frontend/src/i18n/translations.ts`
Dentro del objeto `es` añade estas claves (y sus equivalentes en `en`), sin tocar las existentes:

es:
```
    "spark.title": "¿Qué quieres descubrir hoy?",
    "spark.placeholder": "Escribe tu pregunta…",
    "spark.discover": "¡Descubrir!",
    "spark.suggestions": "Islas para empezar…",
    "spark.blocked": "Esta la vemos con un adulto.",
```
en:
```
    "spark.title": "What do you want to discover today?",
    "spark.placeholder": "Type your question…",
    "spark.discover": "Discover!",
    "spark.suggestions": "Islands to start…",
    "spark.blocked": "Let's see this one with a grown-up.",
```

## Step 2: Test `frontend/src/screens/Spark.test.tsx`

```tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setToken } from "../api/client";
import Spark from "./Spark";

beforeEach(() => {
  localStorage.clear();
  setToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

test("submitting a curiosity creates a lesson", async () => {
  const fetchMock = vi.fn(async (url: string) => {
    if (String(url).includes("/me/suggestions")) {
      return new Response(JSON.stringify([{ curiosity: "¿por qué llueve?", emoji: "🌧️" }]), { status: 200 });
    }
    return new Response(
      JSON.stringify({
        id: 7, curiosity: "x", subject: "ciencia", concept: "c", title: "t",
        body: "b", fun_fact: "f", answered: false, quiz: { question: "q", options: ["a", "b", "c"] },
      }),
      { status: 201 },
    );
  });
  vi.stubGlobal("fetch", fetchMock);
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <Spark />
      </MemoryRouter>
    </I18nProvider>,
  );
  await userEvent.type(screen.getByRole("textbox"), "¿por qué el cielo es azul?");
  await userEvent.click(screen.getByRole("button", { name: /descubrir/i }));
  await waitFor(() =>
    expect(fetchMock.mock.calls.some((c) => String(c[0]).endsWith("/lessons"))).toBe(true),
  );
});
```

## Step 3: Crear `frontend/src/screens/Spark.tsx`

```tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createLesson, getSuggestions, type Suggestion } from "../api/nucleo";
import { ApiError } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

export default function Spark() {
  const [curiosity, setCuriosity] = useState("");
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { t } = useI18n();
  const navigate = useNavigate();

  useEffect(() => {
    getSuggestions().then(setSuggestions).catch(() => undefined);
  }, []);

  async function start(text: string) {
    if (!text.trim()) return;
    setError("");
    setBusy(true);
    try {
      const lesson = await createLesson(text);
      navigate(`/jugar/leccion/${lesson.id}`);
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 422 ? t("spark.blocked") : t("createFamily.error"),
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <h1>{t("spark.title")}</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          void start(curiosity);
        }}
        style={{ display: "flex", flexDirection: "column", gap: 12 }}
      >
        <input
          value={curiosity}
          onChange={(e) => setCuriosity(e.target.value)}
          placeholder={t("spark.placeholder")}
          aria-label={t("spark.placeholder")}
        />
        {error && <p role="alert" style={{ color: "#fff", fontWeight: 700 }}>{error}</p>}
        <Button type="submit" disabled={busy}>
          🧭 {t("spark.discover")}
        </Button>
      </form>
      <div style={{ fontWeight: 800, color: "#0a5a53", marginTop: 4 }}>{t("spark.suggestions")}</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {suggestions.map((s) => (
          <button key={s.curiosity} onClick={() => void start(s.curiosity)} style={{ textAlign: "left", padding: 13 }}>
            {s.emoji} {s.curiosity}
          </button>
        ))}
      </div>
    </ScreenCard>
  );
}
```

## Step 4: Test + suite
`npm test src/screens/Spark.test.tsx` → PASS. Luego `npm test` completo → todo PASS. Y `npm run lint` → limpio.

## Step 5: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): Spark screen (curiosity + suggestions)"
```
