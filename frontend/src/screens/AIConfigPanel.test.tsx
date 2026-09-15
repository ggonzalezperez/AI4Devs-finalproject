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
  image_providers: [
    { id: "none", label: "Sin imágenes", tier: "free", needs_key: false, needs_base_url: false, enabled: true, models: [] },
    { id: "huggingface", label: "HuggingFace", tier: "free", needs_key: true, needs_base_url: false, enabled: true, models: ["black-forest-labs/FLUX.1-schnell"] },
  ],
};
const CONFIG = { tier: "free", provider: "stub", model: null, base_url: null, has_api_key: false, monthly_quota: 0, used_count: 0, image_provider: "none", image_model: null, image_base_url: null, image_enabled: false, has_image_api_key: false };

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
  const providerSelects = await screen.findAllByLabelText("Proveedor");
  const providerSelect = providerSelects[0];
  await userEvent.selectOptions(providerSelect, "claude");
  await userEvent.type(screen.getByLabelText("Clave API"), "sk-ant-xyz");
  // Hay dos botones "Guardar" (texto e imagen); el de texto es el primero.
  await userEvent.click(screen.getAllByRole("button", { name: /guardar/i })[0]);
  await waitFor(() => expect(put).toHaveBeenCalled());
  const sent = put.mock.calls[0][0];
  expect(sent.provider).toBe("claude");
  expect(sent.api_key).toBe("sk-ant-xyz");
});

test("shows image config section", async () => {
  mockFetch();
  setup();
  expect(await screen.findByText(/Imágenes en las lecciones/i)).toBeInTheDocument();
});
