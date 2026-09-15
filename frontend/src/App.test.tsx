import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { SessionProvider } from "./auth/SessionContext";
import { I18nProvider } from "./i18n/I18nContext";
import App from "./App";

test("shows welcome screen at root", () => {
  localStorage.clear();
  render(
    <I18nProvider initialLang="es">
      <SessionProvider>
        <MemoryRouter initialEntries={["/"]}>
          <App />
        </MemoryRouter>
      </SessionProvider>
    </I18nProvider>,
  );
  expect(screen.getByRole("link", { name: /crear el espacio de mi familia/i })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /ya tengo cuenta/i })).toBeInTheDocument();
});

test("shows registration form at /crear", () => {
  localStorage.clear();
  render(
    <I18nProvider initialLang="es">
      <SessionProvider>
        <MemoryRouter initialEntries={["/crear"]}>
          <App />
        </MemoryRouter>
      </SessionProvider>
    </I18nProvider>,
  );
  expect(screen.getByText(/crea el espacio de tu familia/i)).toBeInTheDocument();
});
