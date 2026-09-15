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
  const init = (spy.mock.calls[0] as unknown as [string, RequestInit])[1];
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
