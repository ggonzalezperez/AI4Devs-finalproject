# Task D2: Panel de configuración de IA (padres) + ruta + enlace + i18n

Frontend `frontend/`. Rama `feature-entrega4-ai-config`. SIN push.

**Files:**
- Create: `frontend/src/screens/AIConfigPanel.tsx`
- Modify: `frontend/src/i18n/translations.ts` (claves `aiPanel.*` en es y en)
- Modify: `frontend/src/App.tsx` (ruta `/familia/ia` protegida)
- Modify: `frontend/src/screens/WhoExplores.tsx` (enlace al panel)
- Test: `frontend/src/screens/AIConfigPanel.test.tsx`

## Step 1: Claves i18n (añadir dentro de `es` y `en`, sin tocar las existentes)
es:
```
    "aiPanel.title": "Configuración de IA",
    "aiPanel.subtitle": "Elige cómo se generan las lecciones.",
    "aiPanel.provider": "Proveedor",
    "aiPanel.model": "Modelo",
    "aiPanel.baseUrl": "URL del servidor (Ollama)",
    "aiPanel.apiKey": "Clave API",
    "aiPanel.apiKeySaved": "•••• (guardada)",
    "aiPanel.save": "Guardar",
    "aiPanel.saved": "Guardado",
    "aiPanel.error": "No se pudo guardar",
    "aiPanel.soon": "próximamente",
    "aiPanel.hardware": "¿Tu equipo puede con un modelo local?",
    "aiPanel.vram": "VRAM (GB)",
    "aiPanel.ram": "RAM (GB)",
    "aiPanel.recommend": "Recomendar",
    "aiPanel.recommended": "Recomendado",
    "aiPanel.link": "⚙️ Configurar IA",
```
en:
```
    "aiPanel.title": "AI settings",
    "aiPanel.subtitle": "Choose how lessons are generated.",
    "aiPanel.provider": "Provider",
    "aiPanel.model": "Model",
    "aiPanel.baseUrl": "Server URL (Ollama)",
    "aiPanel.apiKey": "API key",
    "aiPanel.apiKeySaved": "•••• (saved)",
    "aiPanel.save": "Save",
    "aiPanel.saved": "Saved",
    "aiPanel.error": "Could not save",
    "aiPanel.soon": "coming soon",
    "aiPanel.hardware": "Can your machine run a local model?",
    "aiPanel.vram": "VRAM (GB)",
    "aiPanel.ram": "RAM (GB)",
    "aiPanel.recommend": "Recommend",
    "aiPanel.recommended": "Recommended",
    "aiPanel.link": "⚙️ AI settings",
```

## Step 2: Crear `frontend/src/screens/AIConfigPanel.tsx`
```tsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getAIConfig,
  getCatalog,
  putAIConfig,
  recommendHardware,
  type AIConfig,
  type Catalog,
  type Recommendation,
} from "../api/aiConfig";
import { ApiError } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

export default function AIConfigPanel() {
  const { t } = useI18n();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [provider, setProvider] = useState("stub");
  const [model, setModel] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [hasKey, setHasKey] = useState(false);
  const [vram, setVram] = useState("");
  const [ram, setRam] = useState("");
  const [rec, setRec] = useState<Recommendation | null>(null);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getCatalog().then(setCatalog).catch(() => undefined);
    getAIConfig()
      .then((c: AIConfig) => {
        setProvider(c.provider);
        setModel(c.model ?? "");
        setBaseUrl(c.base_url ?? "");
        setHasKey(c.has_api_key);
      })
      .catch(() => undefined);
  }, []);

  if (!catalog) {
    return (
      <ScreenCard>
        <p>…</p>
      </ScreenCard>
    );
  }

  const providers = catalog.providers;
  const current = providers.find((p) => p.id === provider);
  const tier = current?.tier ?? "free";
  const modelOptions =
    provider === "ollama" ? catalog.ollama_models.map((m) => m.id) : current?.models ?? [];

  async function save() {
    setError("");
    setSaved(false);
    try {
      const cfg = await putAIConfig({
        tier,
        provider,
        model: model || null,
        base_url: provider === "ollama" ? baseUrl || null : null,
        api_key: apiKey ? apiKey : undefined,
      });
      setHasKey(cfg.has_api_key);
      setApiKey("");
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("aiPanel.error"));
    }
  }

  async function doRecommend() {
    try {
      setRec(await recommendHardware(Number(vram) || 0, Number(ram) || 0));
    } catch {
      /* ignore */
    }
  }

  return (
    <ScreenCard>
      <Link to="/familia/explorar">←</Link>
      <h1>{t("aiPanel.title")}</h1>
      <p style={{ color: "#0a5a53", fontWeight: 600 }}>{t("aiPanel.subtitle")}</p>

      <div style={{ display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 16, padding: 16 }}>
        <label>
          {t("aiPanel.provider")}
          <select
            value={provider}
            onChange={(e) => {
              setProvider(e.target.value);
              setModel("");
            }}
          >
            {providers.map((p) => (
              <option key={p.id} value={p.id} disabled={!p.enabled}>
                {p.label} ({p.tier}){p.enabled ? "" : ` — ${t("aiPanel.soon")}`}
              </option>
            ))}
          </select>
        </label>

        {modelOptions.length > 0 && (
          <label>
            {t("aiPanel.model")}
            <select value={model} onChange={(e) => setModel(e.target.value)}>
              <option value="">—</option>
              {modelOptions.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </label>
        )}

        {current?.needs_base_url && (
          <label>
            {t("aiPanel.baseUrl")}
            <input
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder="http://localhost:11434"
            />
          </label>
        )}

        {current?.needs_key && (
          <label>
            {t("aiPanel.apiKey")}
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={hasKey ? t("aiPanel.apiKeySaved") : "sk-..."}
            />
          </label>
        )}

        {error && <p role="alert" style={{ color: "#c0392b", fontWeight: 700, margin: 0 }}>{error}</p>}
        {saved && <p style={{ color: "var(--green)", fontWeight: 700, margin: 0 }}>{t("aiPanel.saved")} ✓</p>}
        <Button onClick={() => void save()}>{t("aiPanel.save")}</Button>
      </div>

      <div style={{ marginTop: 14, background: "#fff", borderRadius: 16, padding: 16 }}>
        <strong>{t("aiPanel.hardware")}</strong>
        <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
          <input
            aria-label={t("aiPanel.vram")}
            value={vram}
            onChange={(e) => setVram(e.target.value)}
            placeholder={t("aiPanel.vram")}
            inputMode="numeric"
          />
          <input
            aria-label={t("aiPanel.ram")}
            value={ram}
            onChange={(e) => setRam(e.target.value)}
            placeholder={t("aiPanel.ram")}
            inputMode="numeric"
          />
          <button onClick={() => void doRecommend()}>{t("aiPanel.recommend")}</button>
        </div>
        {rec && (
          <div style={{ marginTop: 8 }}>
            <div>
              {t("aiPanel.recommended")}: <strong>{rec.recommended}</strong>
            </div>
            <div style={{ fontSize: 13, color: "#0a5a53" }}>{rec.note}</div>
          </div>
        )}
      </div>
    </ScreenCard>
  );
}
```

## Step 3: Añadir la ruta en `frontend/src/App.tsx`
Importa `import AIConfigPanel from "./screens/AIConfigPanel";` y añade, dentro del bloque `<ProtectedRoute>`, junto a las rutas `/familia/*`:
```tsx
        <Route path="/familia/ia" element={<AIConfigPanel />} />
```
No toques el resto de rutas.

## Step 4: Enlace desde `frontend/src/screens/WhoExplores.tsx`
Añade, junto al `<Link to="/familia/nuevo">` existente, otro enlace al panel (lee el archivo y añádelo sin romper lo demás):
```tsx
      <Link to="/familia/ia" style={{ textAlign: "center", marginTop: 4 }}>
        {t("aiPanel.link")}
      </Link>
```

## Step 5: Test `frontend/src/screens/AIConfigPanel.test.tsx`
```tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setToken } from "../api/client";
import AIConfigPanel from "./AIConfigPanel";

const CATALOG = {
  providers: [
    { id: "stub", label: "Demo", tier: "free", needs_key: false, needs_base_url: false, enabled: true, models: [] },
    { id: "claude", label: "Claude", tier: "byok", needs_key: true, needs_base_url: false, enabled: true, models: ["claude-haiku-4-5"] },
  ],
  ollama_models: [],
  default_local_model: "qwen3:4b",
};
const CONFIG = { tier: "free", provider: "stub", model: null, base_url: null, has_api_key: false, monthly_quota: 0, used_count: 0 };

beforeEach(() => {
  localStorage.clear();
  setToken("fam-tok");
});
afterEach(() => vi.restoreAllMocks());

function mockFetch() {
  const put = vi.fn();
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, init?: RequestInit) => {
      if (init?.method === "PUT") {
        put(JSON.parse(String(init.body)));
        return new Response(JSON.stringify({ ...CONFIG, tier: "byok", provider: "claude", has_api_key: true }), { status: 200 });
      }
      if (String(url).includes("/catalog")) return new Response(JSON.stringify(CATALOG), { status: 200 });
      return new Response(JSON.stringify(CONFIG), { status: 200 });
    }),
  );
  return put;
}

function setup() {
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <AIConfigPanel />
      </MemoryRouter>
    </I18nProvider>,
  );
}

test("shows providers and saves a BYOK Claude config with key", async () => {
  const put = mockFetch();
  setup();
  const providerSelect = await screen.findByLabelText("Proveedor");
  await userEvent.selectOptions(providerSelect, "claude");
  await userEvent.type(screen.getByLabelText("Clave API"), "sk-ant-xyz");
  await userEvent.click(screen.getByRole("button", { name: /guardar/i }));
  await waitFor(() => expect(put).toHaveBeenCalled());
  const sent = put.mock.calls[0][0];
  expect(sent.provider).toBe("claude");
  expect(sent.api_key).toBe("sk-ant-xyz");
});
```

## Step 6: Tests + suite + lint
`npm test src/screens/AIConfigPanel.test.tsx` → PASS. Luego `npm test` y `npm run lint` → todo verde.

## Step 7: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): parent AI settings panel (provider/model/key + hardware recommender)"
```
