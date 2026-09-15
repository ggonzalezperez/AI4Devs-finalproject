import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { expect, test } from "vitest";
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
