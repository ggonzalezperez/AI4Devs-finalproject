import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import ChildAccess from "./ChildAccess";

beforeEach(() => localStorage.clear());
afterEach(() => vi.restoreAllMocks());

test("typing 4 digits logs the child in and stores token", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(JSON.stringify({ access_token: "child-tok", token_type: "bearer" }), {
          status: 200,
        }),
    ),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter initialEntries={["/explorar/1"]}>
        <Routes>
          <Route path="/explorar/:childId" element={<ChildAccess />} />
        </Routes>
      </MemoryRouter>
    </I18nProvider>,
  );
  for (const d of ["1", "2", "3", "4"]) {
    await userEvent.click(screen.getByRole("button", { name: d }));
  }
  await waitFor(() => expect(localStorage.getItem("chispa_child_token")).toBe("child-tok"));
});

test("shows a kind waiting message when the PIN endpoint answers 429", async () => {
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
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter initialEntries={["/explorar/1"]}>
        <Routes>
          <Route path="/explorar/:childId" element={<ChildAccess />} />
        </Routes>
      </MemoryRouter>
    </I18nProvider>,
  );
  for (const d of ["1", "2", "3", "4"]) {
    await userEvent.click(screen.getByRole("button", { name: d }));
  }
  // Nada de jerga de seguridad: el niño solo entiende que toca esperar.
  expect(await screen.findByText(/espera un poquito/i)).toBeInTheDocument();
});
