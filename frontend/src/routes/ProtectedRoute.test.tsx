import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, expect, test } from "vitest";
import { SessionProvider } from "../auth/SessionContext";
import { setToken } from "../api/client";
import ProtectedRoute from "./ProtectedRoute";

function renderAt(path: string) {
  return render(
    <SessionProvider>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/login" element={<div>login page</div>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/familia" element={<div>panel</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </SessionProvider>,
  );
}

beforeEach(() => localStorage.clear());

test("redirects to /login when not authenticated", () => {
  renderAt("/familia");
  expect(screen.getByText("login page")).toBeInTheDocument();
});

test("renders protected content when authenticated", () => {
  setToken("tok");
  renderAt("/familia");
  expect(screen.getByText("panel")).toBeInTheDocument();
});
