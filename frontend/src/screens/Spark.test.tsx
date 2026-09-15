import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { setChildToken } from "../api/client";
import Spark from "./Spark";

beforeEach(() => {
  localStorage.clear();
  setChildToken("child-tok");
});
afterEach(() => vi.restoreAllMocks());

test("submitting a curiosity creates a lesson", async () => {
  const fetchMock = vi.fn(async (url: string) => {
    if (String(url).includes("/me/suggestions")) {
      return new Response(JSON.stringify([{ curiosity: "¿por qué llueve?", emoji: "🌧️" }]), { status: 200 });
    }
    return new Response(
      JSON.stringify({
        id: 7, curiosity: "x", subject: "ciencia", concept: "c", title: "t",
        body: "b", fun_fact: "f", answered: false, quiz: { question: "q", options: ["a", "b", "c"] },
      }),
      { status: 201 },
    );
  });
  vi.stubGlobal("fetch", fetchMock);
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <Spark />
      </MemoryRouter>
    </I18nProvider>,
  );
  await userEvent.type(screen.getByRole("textbox"), "¿por qué el cielo es azul?");
  await userEvent.click(screen.getByRole("button", { name: /descubrir/i }));
  await waitFor(() =>
    expect(fetchMock.mock.calls.some((c) => String(c[0]).endsWith("/lessons"))).toBe(true),
  );
});

test("mientras espera la lección avisa de que está pensando", async () => {
  // Petición que no resuelve: así se observa el estado de espera.
  vi.stubGlobal("fetch", vi.fn(() => new Promise(() => {})));
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <Spark />
      </MemoryRouter>
    </I18nProvider>,
  );

  fireEvent.change(screen.getByLabelText(/escribe tu pregunta/i), {
    target: { value: "por que llueve" },
  });
  fireEvent.click(screen.getByRole("button", { name: /descubrir/i }));

  expect(await screen.findByRole("status")).toHaveTextContent(/pensando/i);
});
