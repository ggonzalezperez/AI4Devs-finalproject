import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import Button from "./Button";

test("calls onClick when pressed", async () => {
  const onClick = vi.fn();
  render(<Button onClick={onClick}>Crear cuenta</Button>);
  await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
  expect(onClick).toHaveBeenCalledOnce();
});

test("does not call onClick when disabled", async () => {
  const onClick = vi.fn();
  render(
    <Button onClick={onClick} disabled>
      Crear cuenta
    </Button>,
  );
  await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
  expect(onClick).not.toHaveBeenCalled();
});
