import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { getChildToken, setChildToken, setToken } from "../api/client";
import ExitChildSession from "./ExitChildSession";

beforeEach(() => {
  localStorage.clear();
  setToken("family-tok");
  setChildToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

function pantalla() {
  return render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <ExitChildSession />
      </MemoryRouter>
    </I18nProvider>,
  );
}

test("con la contraseña correcta cierra la sesión del niño", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ status: "ok" }), { status: 200 })));
  pantalla();

  fireEvent.change(screen.getByLabelText(/contraseña/i), { target: { value: "secret123" } });
  fireEvent.click(screen.getByRole("button", { name: /salir/i }));

  await waitFor(() => expect(getChildToken()).toBeNull());
});

test("con la contraseña incorrecta NO cierra la sesión del niño", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify({ detail: "Contraseña incorrecta" }), { status: 401 })),
  );
  pantalla();

  fireEvent.change(screen.getByLabelText(/contraseña/i), { target: { value: "loquesea" } });
  fireEvent.click(screen.getByRole("button", { name: /salir/i }));

  expect(await screen.findByRole("alert")).toHaveTextContent(/incorrecta/i);
  expect(getChildToken()).toBe("child-tok");
});
