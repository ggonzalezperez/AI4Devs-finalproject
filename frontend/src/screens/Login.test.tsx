import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { SessionProvider } from "../auth/SessionContext";
import Login from "./Login";

beforeEach(() => localStorage.clear());
afterEach(() => vi.restoreAllMocks());

function setup() {
  render(
    <I18nProvider initialLang="es">
      <SessionProvider>
        <MemoryRouter>
          <Login />
        </MemoryRouter>
      </SessionProvider>
    </I18nProvider>,
  );
}

async function fillForm() {
  await userEvent.type(screen.getByLabelText("Email"), "ana@x.com");
  await userEvent.type(screen.getByLabelText("Contraseña"), "secret123");
}

test("logs in and stores the token", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(JSON.stringify({ access_token: "t1", token_type: "bearer" }), { status: 200 }),
    ),
  );
  setup();
  await fillForm();
  await userEvent.click(screen.getByRole("button", { name: /entrar/i }));
  await waitFor(() => expect(localStorage.getItem("chispa_token")).toBe("t1"));
});

test("shows the too many attempts message on 429", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(JSON.stringify({ detail: "Demasiados intentos." }), {
          status: 429,
          headers: { "Retry-After": "60" },
        }),
    ),
  );
  setup();
  await fillForm();
  await userEvent.click(screen.getByRole("button", { name: /entrar/i }));
  // No debe decir "contraseña incorrecta": el intento ni siquiera se evaluó.
  expect(await screen.findByText(/demasiados intentos/i)).toBeInTheDocument();
});
