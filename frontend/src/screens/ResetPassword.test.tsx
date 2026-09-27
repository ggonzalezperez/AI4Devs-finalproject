import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { expect, test, vi } from "vitest";
import userEvent from "@testing-library/user-event";
import { I18nProvider } from "../i18n/I18nContext";
import { SessionProvider } from "../auth/SessionContext";
import ResetPassword from "./ResetPassword";

function setup() {
  render(
    <I18nProvider initialLang="es">
      <SessionProvider>
        <MemoryRouter>
          <ResetPassword />
        </MemoryRouter>
      </SessionProvider>
    </I18nProvider>,
  );
}

test("renders reset password form", () => {
  setup();
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/código de recuperación/i)).toBeInTheDocument();
  expect(screen.getAllByLabelText(/nueva contraseña/i).length).toBeGreaterThanOrEqual(1);
  expect(screen.getByRole("button", { name: /restablecer contraseña/i })).toBeInTheDocument();
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
  await userEvent.type(screen.getByLabelText(/email/i), "ana@x.com");
  await userEvent.type(screen.getByLabelText(/código de recuperación/i), "AAAA-BBBB");
  const contrasenas = screen.getAllByLabelText(/contraseña/i);
  await userEvent.type(contrasenas[0], "nueva-larga-1");
  await userEvent.type(contrasenas[1], "nueva-larga-1");
  await userEvent.click(screen.getByRole("button", { name: /restablecer contraseña/i }));
  expect(await screen.findByText(/demasiados intentos/i)).toBeInTheDocument();
});
