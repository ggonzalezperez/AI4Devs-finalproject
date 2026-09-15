import { render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import SpeakButton from "./SpeakButton";

afterEach(() => vi.unstubAllGlobals());

test("renders nothing when speech synthesis is unsupported", () => {
  // jsdom no define speechSynthesis
  const { container } = render(
    <I18nProvider initialLang="es">
      <SpeakButton text="hola" />
    </I18nProvider>,
  );
  expect(container.querySelector("button")).toBeNull();
});

test("shows the listen button when supported", () => {
  vi.stubGlobal("speechSynthesis", { speak: () => {}, cancel: () => {}, speaking: false });
  vi.stubGlobal("SpeechSynthesisUtterance", class { lang = ""; rate = 1; onend = null; onerror = null; constructor(public text: string) {} });
  render(
    <I18nProvider initialLang="es">
      <SpeakButton text="hola" />
    </I18nProvider>,
  );
  expect(screen.getByRole("button", { name: /escuchar la lección/i })).toBeInTheDocument();
});
