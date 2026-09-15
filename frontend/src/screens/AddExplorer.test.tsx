import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import AddExplorer from "./AddExplorer";

beforeEach(() => localStorage.clear());
afterEach(() => vi.restoreAllMocks());

function setup() {
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <AddExplorer />
      </MemoryRouter>
    </I18nProvider>,
  );
}

test("shows error when the two PINs do not match", async () => {
  setup();
  await userEvent.type(screen.getByLabelText("Alias"), "Leo");
  await userEvent.type(screen.getByLabelText(/Clave de 4 dígitos/i), "1234");
  await userEvent.type(screen.getByLabelText("Repite la clave"), "5678");
  await userEvent.click(screen.getByRole("button", { name: /guardar explorador/i }));
  expect(await screen.findByText(/no coinciden/i)).toBeInTheDocument();
});

test("sends chosen avatar in POST body", async () => {
  const fetchMock = vi.fn(
    async () =>
      new Response(
        JSON.stringify({ id: 1, name: "Leo", birthdate: "2020-01-01", age: 5, avatar: "rocket" }),
        { status: 201 },
      ),
  );
  vi.stubGlobal("fetch", fetchMock);
  // need a token so auth header is set
  localStorage.setItem("chispa_token", "parent-tok");
  setup();
  await userEvent.click(screen.getByRole("radio", { name: "Cohete" }));
  await userEvent.type(screen.getByLabelText("Alias"), "Leo");
  await userEvent.type(screen.getByLabelText(/Fecha de nacimiento/i), "2020-01-01");
  await userEvent.type(screen.getByLabelText(/Clave de 4 dígitos/i), "1234");
  await userEvent.type(screen.getByLabelText("Repite la clave"), "1234");
  await userEvent.click(screen.getByRole("button", { name: /guardar explorador/i }));
  await waitFor(() => expect(fetchMock).toHaveBeenCalled());
  const call = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
  const body = JSON.parse(call[1].body as string);
  expect(body.avatar).toBe("rocket");
});
