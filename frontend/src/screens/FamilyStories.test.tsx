import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setToken } from "../api/client";
import FamilyStories from "./FamilyStories";

beforeEach(() => {
  localStorage.clear();
  setToken("fam-tok");
});
afterEach(() => vi.restoreAllMocks());

test("shows a pending story with approve control", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(
        JSON.stringify([{ id: 3, title: "Cuento de Leo", body: "Érase una vez...", status: "pending" }]),
        { status: 200 },
      ),
    ),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <FamilyStories />
      </MemoryRouter>
    </I18nProvider>,
  );
  expect(await screen.findByDisplayValue("Cuento de Leo")).toBeInTheDocument();
  expect(screen.getByText(/Aprobar/)).toBeInTheDocument();
});
