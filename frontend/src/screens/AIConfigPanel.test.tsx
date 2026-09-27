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

function mockFetch(configOverrides: Partial<typeof CONFIG> = {}) {
  const put = vi.fn();
  const config = { ...CONFIG, ...configOverrides };
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, init?: RequestInit) => {
      if (init?.method === "PUT") {
        put(JSON.parse(String(init.body)));
        return new Response(JSON.stringify({ ...config, tier: "byok", provider: "claude", has_api_key: true }), { status: 200 });
      }
      if (String(url).includes("/catalog")) return new Response(JSON.stringify(CATALOG), { status: 200 });
      return new Response(JSON.stringify(config), { status: 200 });
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

test("avisa al abrir una configuración con proveedor de imagen y las imágenes apagadas", async () => {
  // El fallo que esto cierra: se podía guardar proveedor y clave con la casilla
  // desactivada y el panel no decía nada, así que la familia creía tener
  // ilustraciones y las lecciones salían sin ninguna. Al derivarse del render y no
  // del guardado, el aviso aparece también al ABRIR el panel, que es el caso en el
  // que el fallo llevaba invisible desde el 15-09.
  mockFetch({ image_provider: "huggingface", has_image_api_key: true, image_enabled: false });
  setup();
  const aviso = await screen.findByRole("status");
  expect(aviso).toHaveTextContent(/imágenes están desactivadas/i);
  // Y no filtra la clave: solo dice que hay una guardada.
  expect(aviso.textContent).not.toMatch(/hf_|sk-/);
});

test("no avisa en el estado por defecto ni con las imágenes activadas", async () => {
  // Sin este caso el aviso saldría a TODAS las familias: el estado por defecto es
  // precisamente proveedor «none» con las imágenes apagadas (RF-PLT-03), y un aviso
  // que sale siempre es ruido que se aprende a ignorar.
  mockFetch();
  setup();
  expect(await screen.findByText(/Imágenes en las lecciones/i)).toBeInTheDocument();
  expect(screen.queryByRole("status")).not.toBeInTheDocument();

  // Y con proveedor elegido y las imágenes activadas tampoco: no hay nada que avisar.
  vi.restoreAllMocks();
  mockFetch({ image_provider: "huggingface", image_enabled: true });
  setup();
  await waitFor(() => expect(screen.queryByRole("status")).not.toBeInTheDocument());
});
