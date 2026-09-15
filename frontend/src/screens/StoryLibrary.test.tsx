import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setChildToken } from "../api/client";
import StoryLibrary from "./StoryLibrary";

beforeEach(() => {
  localStorage.clear();
  setChildToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

test("lists approved stories", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(
        JSON.stringify([{ id: 7, title: "La aventura de Leo", body: "...", status: "approved" }]),
        { status: 200 },
      ),
    ),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <StoryLibrary />
      </MemoryRouter>
    </I18nProvider>,
  );
  expect(await screen.findByText("La aventura de Leo")).toBeInTheDocument();
});
