import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, test } from "vitest";
import { SessionProvider, useSession } from "./SessionContext";

function Probe() {
  const { isAuthenticated, login, logout } = useSession();
  return (
    <div>
      <span>{isAuthenticated ? "in" : "out"}</span>
      <button onClick={() => login("tok")}>login</button>
      <button onClick={logout}>logout</button>
    </div>
  );
}

beforeEach(() => localStorage.clear());

test("login and logout toggle authentication", async () => {
  render(
    <SessionProvider>
      <Probe />
    </SessionProvider>,
  );
  expect(screen.getByText("out")).toBeInTheDocument();
  await userEvent.click(screen.getByText("login"));
  expect(screen.getByText("in")).toBeInTheDocument();
  await userEvent.click(screen.getByText("logout"));
  expect(screen.getByText("out")).toBeInTheDocument();
});
