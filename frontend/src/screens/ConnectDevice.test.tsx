import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { expect, test } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import ConnectDevice from "./ConnectDevice";

test("shows the app URL and a QR code", () => {
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <ConnectDevice />
      </MemoryRouter>
    </I18nProvider>,
  );
  // En jsdom, window.location.origin suele ser http://localhost:3000
  expect(screen.getByText(/conectar otro dispositivo/i)).toBeInTheDocument();
  expect(screen.getByText(new RegExp(window.location.origin.replace(/[.]/g, "\\."), "i"))).toBeInTheDocument();
  expect(document.querySelector("svg")).not.toBeNull(); // el QR es un <svg>
});
