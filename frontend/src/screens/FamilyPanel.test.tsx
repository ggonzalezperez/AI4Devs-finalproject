import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setToken } from "../api/client";
import FamilyPanel from "./FamilyPanel";

const NORA = { id: 1, name: "Nora", birthdate: "2018-01-01", age: 7, avatar: "fox", avatar_image_url: null };
const LEO = { id: 2, name: "Leo", birthdate: "2021-03-01", age: 4, avatar: "cat", avatar_image_url: null };

/** Responde según la ruta pedida: hijos, perfil o ficha. */
function stubApi(porNino: Record<number, { perfil: unknown; ficha: unknown }>) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      const ruta = String(url);
      const m = ruta.match(/\/children\/(\d+)\/(profile|knowledge)/);
      if (m) {
        const datos = porNino[Number(m[1])];
        return new Response(JSON.stringify(m[2] === "profile" ? datos.perfil : datos.ficha), { status: 200 });
      }
      return new Response(JSON.stringify(Object.keys(porNino).map((id) => (Number(id) === 1 ? NORA : LEO))), { status: 200 });
    }),
  );
}

beforeEach(() => {
  localStorage.clear();
  setToken("family-tok");
});
afterEach(() => vi.restoreAllMocks());

test("separa conceptos fuertes de emergentes según la maestría", async () => {
  stubApi({
    1: {
      perfil: { name: "Nora", age: 7, islands: 2, avatar: "fox", avatar_image_url: null },
      ficha: [
        { id: 10, concept: "flotabilidad", subject: "ciencia", mastery: 3, root_lesson_id: 9 },
        { id: 11, concept: "volcanes", subject: "ciencia", mastery: 1, root_lesson_id: 12 },
      ],
    },
  });

  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <FamilyPanel />
      </MemoryRouter>
    </I18nProvider>,
  );

  // mastery >= 2 es fuerte; mastery == 1 es emergente (solo el reto acertado sube maestría).
  const fuertes = await screen.findByTestId("conceptos-fuertes");
  const emergentes = await screen.findByTestId("conceptos-emergentes");
  expect(fuertes).toHaveTextContent("flotabilidad");
  expect(fuertes).not.toHaveTextContent("volcanes");
  expect(emergentes).toHaveTextContent("volcanes");
  expect(emergentes).not.toHaveTextContent("flotabilidad");
});

test("el selector cambia de hijo sin mezclar datos entre hermanos", async () => {
  stubApi({
    1: {
      perfil: { name: "Nora", age: 7, islands: 1, avatar: "fox", avatar_image_url: null },
      ficha: [{ id: 10, concept: "flotabilidad", subject: "ciencia", mastery: 3, root_lesson_id: 9 }],
    },
    2: {
      perfil: { name: "Leo", age: 4, islands: 1, avatar: "cat", avatar_image_url: null },
      ficha: [{ id: 20, concept: "dinosaurios", subject: "ciencia", mastery: 1, root_lesson_id: 21 }],
    },
  });

  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <FamilyPanel />
      </MemoryRouter>
    </I18nProvider>,
  );

  expect(await screen.findByText("flotabilidad")).toBeInTheDocument();

  fireEvent.click(await screen.findByRole("button", { name: /leo/i }));

  expect(await screen.findByText("dinosaurios")).toBeInTheDocument();
  expect(screen.queryByText("flotabilidad")).not.toBeInTheDocument();
});

test("ofrece la flecha de volver arriba, como el resto de pantallas de familia", async () => {
  stubApi({
    1: {
      perfil: { name: "Nora", age: 7, islands: 0, avatar: "fox", avatar_image_url: null },
      ficha: [],
    },
  });

  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <FamilyPanel />
      </MemoryRouter>
    </I18nProvider>,
  );

  const volver = await screen.findByRole("link", { name: "←" });
  expect(volver).toHaveAttribute("href", "/familia/explorar");
});
