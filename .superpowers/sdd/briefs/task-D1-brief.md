# Task D1: Cliente API de configuración de IA (frontend)

Frontend `frontend/`. Rama `feature-entrega4-ai-config`. SIN push.

**Files:**
- Create: `frontend/src/api/aiConfig.ts`
- Test: `frontend/src/api/aiConfig.test.ts`

## Step 1: Crear `frontend/src/api/aiConfig.ts`
```ts
import { apiFetch } from "./client";

export type AIConfig = {
  tier: string;
  provider: string;
  model: string | null;
  base_url: string | null;
  has_api_key: boolean;
  monthly_quota: number;
  used_count: number;
};

export type Provider = {
  id: string;
  label: string;
  tier: string;
  needs_key: boolean;
  needs_base_url: boolean;
  enabled: boolean;
  models: string[];
};

export type OllamaModel = {
  id: string;
  label: string;
  min_vram_gb: number;
  min_ram_gb: number;
  speed: string;
};

export type Catalog = {
  providers: Provider[];
  ollama_models: OllamaModel[];
  default_local_model: string;
};

export type Recommendation = {
  can_run_local: boolean;
  fits: string[];
  recommended: string;
  note: string;
};

export type AIConfigUpdate = {
  tier: string;
  provider: string;
  model?: string | null;
  base_url?: string | null;
  api_key?: string | null;
};

export function getAIConfig() {
  return apiFetch<AIConfig>("/family/ai-config", { auth: true });
}

export function putAIConfig(payload: AIConfigUpdate) {
  return apiFetch<AIConfig>("/family/ai-config", { method: "PUT", auth: true, body: payload });
}

export function getCatalog() {
  return apiFetch<Catalog>("/family/ai-config/catalog", { auth: true });
}

export function recommendHardware(vram_gb: number, ram_gb: number) {
  return apiFetch<Recommendation>("/family/ai-config/recommend", {
    method: "POST",
    auth: true,
    body: { vram_gb, ram_gb },
  });
}
```

## Step 2: Test `frontend/src/api/aiConfig.test.ts`
```ts
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { getCatalog, putAIConfig } from "./aiConfig";
import { setToken } from "./client";

beforeEach(() => {
  localStorage.clear();
  setToken("fam-tok");
});
afterEach(() => vi.restoreAllMocks());

test("getCatalog returns providers with auth", async () => {
  const spy = vi.fn(
    async () =>
      new Response(
        JSON.stringify({
          providers: [{ id: "claude", label: "Claude", tier: "byok", needs_key: true, needs_base_url: false, enabled: true, models: ["claude-haiku-4-5"] }],
          ollama_models: [],
          default_local_model: "qwen3:4b",
        }),
        { status: 200 },
      ),
  );
  vi.stubGlobal("fetch", spy);
  const cat = await getCatalog();
  expect(cat.providers[0].id).toBe("claude");
  const init = spy.mock.calls[0][1] as RequestInit;
  expect((init.headers as Record<string, string>).Authorization).toBe("Bearer fam-tok");
});

test("putAIConfig sends PUT and returns config", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(
        JSON.stringify({ tier: "byok", provider: "claude", model: "claude-haiku-4-5", base_url: null, has_api_key: true, monthly_quota: 0, used_count: 0 }),
        { status: 200 },
      ),
    ),
  );
  const cfg = await putAIConfig({ tier: "byok", provider: "claude", model: "claude-haiku-4-5", api_key: "sk-ant" });
  expect(cfg.has_api_key).toBe(true);
});
```

## Step 3: Tests + suite
`npm test src/api/aiConfig.test.ts` → PASS. Luego `npm test` completo + `npm run lint` → todo verde.

## Step 4: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): AI config API client"
```
