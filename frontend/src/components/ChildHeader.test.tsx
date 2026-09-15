import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setChildToken } from "../api/client";
import ChildHeader from "./ChildHeader";

beforeEach(() => {
  localStorage.clear();
  setChildToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

test("shows child name and islands", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify({ name: "Nora", age: 7, islands: 3, avatar: "cat", avatar_image_url: null }), { status: 200 })),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <ChildHeader />
      </MemoryRouter>
    </I18nProvider>,
  );
  expect(await screen.findByText(/Nora/)).toBeInTheDocument();
  expect(screen.getByText(/🏝️ 3/)).toBeInTheDocument();
});
