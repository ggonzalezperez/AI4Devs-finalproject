import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, test } from "vitest";
import { I18nProvider, detectLang, useI18n } from "./I18nContext";

function Probe() {
  const { t, setLang, lang } = useI18n();
  return (
    <div>
      <span>{t("createFamily.submit")}</span>
      <span>lang:{lang}</span>
      <button onClick={() => setLang("es")}>to-es</button>
    </div>
  );
}

beforeEach(() => localStorage.clear());

test("detectLang uses stored language when present", () => {
  localStorage.setItem("chispa_lang", "es");
  expect(detectLang()).toBe("es");
});

test("t translates for the active language and switching persists", async () => {
  render(
    <I18nProvider initialLang="en">
      <Probe />
    </I18nProvider>,
  );
  expect(screen.getByText("Create account")).toBeInTheDocument();
  await userEvent.click(screen.getByText("to-es"));
  expect(screen.getByText("Crear cuenta")).toBeInTheDocument();
  expect(localStorage.getItem("chispa_lang")).toBe("es");
});
