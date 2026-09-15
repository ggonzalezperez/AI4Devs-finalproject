import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, expect, test } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { SessionProvider } from "../auth/SessionContext";
import { setToken } from "../api/client";
import Welcome from "./Welcome";

beforeEach(() => localStorage.clear());

function renderAt(entry: string) {
  return render(
    <I18nProvider initialLang="es">
      <SessionProvider>
        <MemoryRouter initialEntries={[entry]}>
          <Routes>
            <Route path="/" element={<Welcome />} />
            <Route path="/familia" element={<div>Zona de familia</div>} />
          </Routes>
        </MemoryRouter>
      </SessionProvider>
    </I18nProvider>,
  );
}

test("offers create and sign-in paths when logged out", () => {
  renderAt("/");
  expect(screen.getByRole("link", { name: /crear el espacio de mi familia/i })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /ya tengo cuenta/i })).toBeInTheDocument();
});

test("redirects an authenticated family to its space", () => {
  setToken("fam-tok");
  renderAt("/");
  expect(screen.getByText("Zona de familia")).toBeInTheDocument();
});
