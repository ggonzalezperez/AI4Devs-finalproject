import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import Thinking from "./Thinking";

test("anuncia que Chispa está pensando, para quien no ve la animación", () => {
  render(
    <I18nProvider initialLang="es">
      <Thinking />
    </I18nProvider>,
  );

  // role="status" lo lee un lector de pantalla sin robar el foco.
  const aviso = screen.getByRole("status");
  expect(aviso).toHaveTextContent(/pensando/i);
});
