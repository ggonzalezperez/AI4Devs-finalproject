import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setToken } from "../api/client";
import FamilyLanding from "./FamilyLanding";

beforeEach(() => {
  localStorage.clear();
  setToken("fam-tok");
});
afterEach(() => vi.restoreAllMocks());

function renderLanding(children: unknown[]) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify(children), { status: 200 })),
  );
  return render(
    <I18nProvider initialLang="es">
      <MemoryRouter initialEntries={["/familia"]}>
        <Routes>
          <Route path="/familia" element={<FamilyLanding />} />
          <Route path="/familia/explorar" element={<div>HUB</div>} />
          <Route path="/explorar/:childId" element={<div>PIN</div>} />
        </Routes>
      </MemoryRouter>
    </I18nProvider>,
  );
}

const kid = (id: number, name: string, avatar: string) => ({
  id,
  name,
  birthdate: "2019-01-01",
  age: 7,
  avatar,
  avatar_image_url: null,
});

test("one child goes straight to the child PIN access", async () => {
  renderLanding([kid(7, "Toni", "frog")]);
  expect(await screen.findByText("PIN")).toBeInTheDocument();
});

test("several children go to the family hub", async () => {
  renderLanding([kid(1, "A", "fox"), kid(2, "B", "cat")]);
  expect(await screen.findByText("HUB")).toBeInTheDocument();
});
