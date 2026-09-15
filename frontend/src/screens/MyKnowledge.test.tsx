import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setChildToken } from "../api/client";
import MyKnowledge from "./MyKnowledge";

beforeEach(() => {
  localStorage.clear();
  setChildToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

test("lists knowledge islands", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(JSON.stringify([{ id: 1, concept: "flotabilidad", subject: "ciencia", mastery: 2, root_lesson_id: 9 }]), { status: 200 }),
    ),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <MyKnowledge />
      </MemoryRouter>
    </I18nProvider>,
  );
  expect(await screen.findByText("flotabilidad")).toBeInTheDocument();
});

test("island with root_lesson_id is a link to its conversation", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(JSON.stringify([{ id: 1, concept: "flotabilidad", subject: "ciencia", mastery: 2, root_lesson_id: 9 }]), { status: 200 }),
    ),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <MyKnowledge />
      </MemoryRouter>
    </I18nProvider>,
  );
  const link = await screen.findByRole("link", { name: /flotabilidad/i });
  expect(link).toHaveAttribute("href", "/jugar/leccion/9");
});

test("island without root_lesson_id is not a link", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(JSON.stringify([{ id: 2, concept: "gravedad", subject: "ciencia", mastery: 1, root_lesson_id: null }]), { status: 200 }),
    ),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <MyKnowledge />
      </MemoryRouter>
    </I18nProvider>,
  );
  expect(await screen.findByText("gravedad")).toBeInTheDocument();
  // Should not be rendered as an anchor link (no role="link" with that name)
  const links = screen.queryAllByRole("link", { name: /gravedad/i });
  expect(links).toHaveLength(0);
});

test("search filters islands by concept (accent- and case-insensitive)", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(
        JSON.stringify([
          { id: 1, concept: "flotabilidad", subject: "ciencia", mastery: 2, root_lesson_id: 9 },
          { id: 2, concept: "volcanes", subject: "geografía", mastery: 1, root_lesson_id: 10 },
        ]),
        { status: 200 },
      ),
    ),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <MyKnowledge />
      </MemoryRouter>
    </I18nProvider>,
  );
  const search = await screen.findByLabelText(/buscar una isla/i);
  fireEvent.change(search, { target: { value: "volca" } });
  expect(screen.getByText("volcanes")).toBeInTheDocument();
  expect(screen.queryByText("flotabilidad")).not.toBeInTheDocument();
});
