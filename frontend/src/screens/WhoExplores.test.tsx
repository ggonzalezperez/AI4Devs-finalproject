import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import WhoExplores from "./WhoExplores";

beforeEach(() => localStorage.clear());
afterEach(() => vi.restoreAllMocks());

test("lists the crew (children) from the API", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(
          JSON.stringify([
            { id: 1, name: "Leo", birthdate: "2019-03-12", age: 7, avatar: "fox", avatar_image_url: null },
            { id: 2, name: "Mía", birthdate: "2020-01-01", age: 6, avatar: "cat", avatar_image_url: null },
          ]),
          { status: 200 },
        ),
    ),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <WhoExplores />
      </MemoryRouter>
    </I18nProvider>,
  );
  expect(await screen.findByText("Leo")).toBeInTheDocument();
  expect(screen.getByText("Mía")).toBeInTheDocument();
  expect(screen.getByLabelText("Zorro")).toBeInTheDocument();
});
