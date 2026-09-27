import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { SessionProvider } from "../auth/SessionContext";
import CreateFamily from "./CreateFamily";

beforeEach(() => localStorage.clear());
afterEach(() => vi.restoreAllMocks());

function setup() {
  render(
    <I18nProvider initialLang="es">
      <SessionProvider>
        <MemoryRouter>
          <CreateFamily />
        </MemoryRouter>
      </SessionProvider>
    </I18nProvider>,
  );
}

async function fillForm() {
  await userEvent.type(screen.getByLabelText("Tu nombre"), "Ana");
  await userEvent.type(screen.getByLabelText("Email"), "ana@x.com");
  await userEvent.type(screen.getByLabelText("Contraseña"), "secret123");
  await userEvent.type(screen.getByLabelText("Repite la contraseña"), "secret123");
}

test("submits registration and stores token", async () => {
  const fetchMock = vi.fn(
    async () =>
      new Response(
        JSON.stringify({ access_token: "t1", token_type: "bearer", recovery_code: "AAAA-BBBB-CCCC-DDDD-EEEE-FFFF-0000-1111" }),
        { status: 201 },
      ),
  );
  vi.stubGlobal("fetch", fetchMock);
  setup();
  await fillForm();
  await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
  // After register, recovery code panel is shown
  await waitFor(() => expect(screen.getByText("AAAA-BBBB-CCCC-DDDD-EEEE-FFFF-0000-1111")).toBeInTheDocument());
  // Click Continue to store token and navigate
  await userEvent.click(screen.getByRole("button", { name: /continuar/i }));
  await waitFor(() => expect(localStorage.getItem("chispa_token")).toBe("t1"));
});

test("shows error when passwords do not match", async () => {
  setup();
  await userEvent.type(screen.getByLabelText("Tu nombre"), "Ana");
  await userEvent.type(screen.getByLabelText("Email"), "ana@x.com");
  await userEvent.type(screen.getByLabelText("Contraseña"), "secret123");
  await userEvent.type(screen.getByLabelText("Repite la contraseña"), "different1");
  await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
  expect(await screen.findByText(/no coinciden/i)).toBeInTheDocument();
});

test("sends the invite code when the field is filled", async () => {
  const fetchMock = vi.fn(
    async (_url: string, _init?: RequestInit) =>
      new Response(
        JSON.stringify({ access_token: "t1", token_type: "bearer", recovery_code: "CODE" }),
        { status: 201 },
      ),
  );
  vi.stubGlobal("fetch", fetchMock);
  setup();
  await fillForm();
  await userEvent.type(screen.getByLabelText(/código de invitación/i), "palabra-secreta");
  await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
  await waitFor(() => expect(fetchMock).toHaveBeenCalled());
  const body = JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body));
  expect(body.invite_code).toBe("palabra-secreta");
});

test("shows the server message when the invite code is rejected", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(JSON.stringify({ detail: "Código de invitación no válido" }), { status: 403 }),
    ),
  );
  setup();
  await fillForm();
  await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
  expect(await screen.findByText(/código de invitación no válido/i)).toBeInTheDocument();
});

test("shows error message when email already exists", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(JSON.stringify({ detail: "Email ya registrado" }), { status: 409 }),
    ),
  );
  setup();
  await fillForm();
  await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
  expect(await screen.findByText(/email ya registrado/i)).toBeInTheDocument();
});
