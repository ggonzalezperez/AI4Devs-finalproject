import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { expect, test } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { SessionProvider } from "../auth/SessionContext";
import ChangePassword from "./ChangePassword";

function setup() {
  render(
    <I18nProvider initialLang="es">
      <SessionProvider>
        <MemoryRouter>
          <ChangePassword />
        </MemoryRouter>
      </SessionProvider>
    </I18nProvider>,
  );
}

test("renders change password form", () => {
  setup();
  expect(screen.getByLabelText(/contraseña actual/i)).toBeInTheDocument();
  expect(screen.getAllByLabelText(/nueva contraseña/i).length).toBeGreaterThanOrEqual(1);
  expect(screen.getByLabelText(/repite la nueva contraseña/i)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /cambiar contraseña/i })).toBeInTheDocument();
});
