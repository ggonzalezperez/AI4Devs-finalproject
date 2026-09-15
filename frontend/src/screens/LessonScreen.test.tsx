import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setChildToken } from "../api/client";
import LessonScreen from "./LessonScreen";

beforeEach(() => {
  localStorage.clear();
  setChildToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

const TURN = {
  id: 5,
  curiosity: "¿por qué llueve?",
  subject: "ciencia",
  concept: "lluvia",
  title: "La lluvia",
  body: "El agua sube en forma de vapor y vuelve a caer.",
  fun_fact: "Una nube pesa toneladas.",
  answered: false,
  follow_ups: ["¿Y la nieve?"],
  quiz: { question: "¿Qué sube al cielo?", options: ["El agua", "La arena", "El fuego"] },
  image_url: null,
};

test("renders the conversation and a follow-up chip", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify([TURN]), { status: 200 })),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter initialEntries={["/jugar/leccion/5"]}>
        <Routes>
          <Route path="/jugar/leccion/:id" element={<LessonScreen />} />
        </Routes>
      </MemoryRouter>
    </I18nProvider>,
  );
  expect(await screen.findByText("La lluvia")).toBeInTheDocument();
  expect(screen.getByText(/El agua sube/)).toBeInTheDocument();
  expect(screen.getByText(/¿Y la nieve\?/)).toBeInTheDocument();
});

test("una ilustración que ya no existe se oculta en vez de salir rota", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(
        JSON.stringify([
          {
            id: 8, curiosity: "perros", subject: "ciencia", concept: "perros",
            title: "Los perros", body: "cuerpo", fun_fact: "dato", answered: false,
            quiz: { question: "q", options: ["a", "b", "c"] }, follow_ups: [],
            image_url: "/media/lessons/8.png",
          },
        ]),
        { status: 200 },
      ),
    ),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter initialEntries={["/jugar/leccion/8"]}>
        <Routes>
          <Route path="/jugar/leccion/:id" element={<LessonScreen />} />
        </Routes>
      </MemoryRouter>
    </I18nProvider>,
  );

  const img = await screen.findByRole("img", { name: /los perros/i });
  // El fichero ya no está (p. ej. se perdió en un redespliegue): el niño no
  // debe ver el icono de imagen rota.
  fireEvent.error(img);
  await waitFor(() => expect(screen.queryByRole("img", { name: /los perros/i })).toBeNull());
});

test("al repreguntar avisa de que está pensando, donde saldrá la respuesta", async () => {
  const turno = {
    id: 1, curiosity: "perros", subject: "ciencia", concept: "perros",
    title: "Los perros", body: "cuerpo", fun_fact: "dato", answered: false,
    quiz: { question: "q", options: ["a", "b", "c"] }, follow_ups: [], image_url: null,
  };
  // Se responde por RUTA, no por orden: ChildHeader pide el perfil a la vez que
  // la pantalla pide el hilo, y contar llamadas hacía el test dependiente del
  // orden en que salieran.
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      const ruta = String(url);
      if (ruta.includes("/thread")) {
        return new Response(JSON.stringify([turno]), { status: 200 });
      }
      if (ruta.includes("/me/profile")) {
        return new Response(
          JSON.stringify({ name: "Nora", age: 8, islands: 1, avatar: "fox", avatar_image_url: null }),
          { status: 200 },
        );
      }
      return new Promise(() => {}) as never; // la repregunta no resuelve
    }),
  );
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter initialEntries={["/jugar/leccion/1"]}>
        <Routes>
          <Route path="/jugar/leccion/:id" element={<LessonScreen />} />
        </Routes>
      </MemoryRouter>
    </I18nProvider>,
  );

  const campo = await screen.findByLabelText(/pregunta lo que quieras/i);
  fireEvent.change(campo, { target: { value: "¿y los gatos?" } });
  fireEvent.submit(campo.closest("form")!);

  expect(await screen.findByRole("status")).toHaveTextContent(/pensando/i);
});
