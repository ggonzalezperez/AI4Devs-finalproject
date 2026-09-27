import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import MicButton from "./MicButton";

afterEach(() => {
  vi.unstubAllGlobals();
});

test("renders nothing when speech recognition is unsupported", () => {
  const { container } = render(
    <I18nProvider initialLang="es">
      <MicButton onText={() => {}} />
    </I18nProvider>,
  );
  expect(container.querySelector("button")).toBeNull();
});

test("shows the mic button when supported", () => {
  class FakeRec {
    lang = "";
    continuous = false;
    interimResults = false;
    onresult = null;
    onend = null;
    onerror = null;
    start() {}
    stop() {}
  }
  vi.stubGlobal("SpeechRecognition", FakeRec);
  render(
    <I18nProvider initialLang="es">
      <MicButton onText={() => {}} />
    </I18nProvider>,
  );
  expect(screen.getByRole("button", { name: /dictar la pregunta/i })).toBeInTheDocument();
});

/** Reconocimiento falso que permite disparar el error que queramos. */
function fakeRecognition() {
  const instancias: any[] = [];
  class FakeRec {
    lang = "";
    continuous = false;
    interimResults = false;
    onresult: any = null;
    onend: any = null;
    onerror: any = null;
    start() {
      instancias.push(this);
    }
    stop() {}
  }
  vi.stubGlobal("SpeechRecognition", FakeRec);
  return instancias;
}

test("si el navegador deniega el micrófono, lo dice en lugar de callarse", async () => {
  const instancias = fakeRecognition();
  render(
    <I18nProvider initialLang="es">
      <MicButton onText={() => {}} />
    </I18nProvider>,
  );

  fireEvent.click(screen.getByRole("button", { name: /dictar la pregunta/i }));
  // El navegador rechaza el permiso.
  instancias[0].onerror({ error: "not-allowed" });

  expect(await screen.findByRole("alert")).toHaveTextContent(/permiso/i);
});

test("en conexión insegura avisa de que no es un permiso, sin pedir permiso imposible", async () => {
  const instancias = fakeRecognition();
  vi.stubGlobal("isSecureContext", false);
  render(
    <I18nProvider initialLang="es">
      <MicButton onText={() => {}} />
    </I18nProvider>,
  );

  fireEvent.click(screen.getByRole("button", { name: /dictar la pregunta/i }));

  // Ni siquiera se intenta arrancar: el navegador no va a pedir permiso.
  expect(instancias).toHaveLength(0);
  expect(await screen.findByRole("alert")).toHaveTextContent(/segura/i);
});

test("envía la pregunta al terminar el dictado, sin pulsar el botón de enviar", async () => {
  const instancias = fakeRecognition();
  const enviado: string[] = [];
  render(
    <I18nProvider initialLang="es">
      <MicButton onText={() => {}} onAutoSubmit={(texto) => enviado.push(texto)} />
    </I18nProvider>,
  );

  fireEvent.click(screen.getByRole("button", { name: /dictar la pregunta/i }));
  instancias[0].onresult({ results: [[{ transcript: "por qué el mar es salado" }]] });

  expect(enviado).toEqual(["por qué el mar es salado"]);
});

test("no envía nada si la transcripción viene vacía", async () => {
  const instancias = fakeRecognition();
  const enviado: string[] = [];
  render(
    <I18nProvider initialLang="es">
      <MicButton onText={() => {}} onAutoSubmit={(texto) => enviado.push(texto)} />
    </I18nProvider>,
  );

  fireEvent.click(screen.getByRole("button", { name: /dictar la pregunta/i }));
  instancias[0].onresult({ results: [[{ transcript: "" }]] });

  expect(enviado).toEqual([]);
});
