# Task 2: Tokens de diseño y primitivas de UI (Button, ScreenCard)

Estas son tus REQUISITOS. Usa el código EXACTO que aparece aquí.

**Files:**
- Create: `frontend/src/styles/theme.css`
- Create: `frontend/src/components/Button.tsx`
- Create: `frontend/src/components/ScreenCard.tsx`
- Test: `frontend/src/components/Button.test.tsx`
- Modify: `frontend/src/main.tsx` (importar theme.css)

**Produces:** CSS vars en `:root` (`--coral`, `--teal`, `--teal-dark`, `--paper`, `--cream`); `Button({children,onClick,type?,disabled?})` (botón coral); `ScreenCard({children})` (contenedor marco móvil).

- [ ] **Step 1: Crear `frontend/src/styles/theme.css`**

```css
@import url("https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Mulish:wght@400;600;700;800&family=Nunito:wght@400;600;700;800&display=swap");

:root {
  --coral: #ff7a59;
  --teal: #0e837b;
  --teal-dark: #08433e;
  --teal-mid: #0e5b56;
  --paper: #e8e6e1;
  --cream: #fbf3e0;
  --green: #2aa06a;
  --amber: #e0892f;
  --font-head: "Fredoka", system-ui, sans-serif;
  --font-body: "Mulish", system-ui, sans-serif;
}

* { box-sizing: border-box; }
body { margin: 0; background: var(--paper); font-family: var(--font-body); color: var(--teal-dark); }

.btn-primary {
  background: var(--coral);
  color: #fff;
  border: none;
  border-radius: 16px;
  padding: 15px;
  width: 100%;
  font-family: var(--font-head);
  font-size: 17px;
  font-weight: 600;
  box-shadow: 0 8px 18px rgba(255, 122, 89, 0.35);
  cursor: pointer;
}
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.screen-card {
  max-width: 360px;
  margin: 0 auto;
  min-height: 640px;
  border-radius: 36px;
  padding: 26px 24px;
  background: radial-gradient(120% 95% at 50% -8%, #aeeae3 0%, #4cc0b6 48%, #0e837b 100%);
  box-shadow: 0 24px 60px rgba(14, 122, 116, 0.3);
}
```

- [ ] **Step 2: Importar el theme en `frontend/src/main.tsx`** (añadir como primera import). El archivo completo debe quedar así:

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles/theme.css";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

- [ ] **Step 3: Crear `frontend/src/components/Button.tsx`**

```tsx
import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  disabled?: boolean;
};

export default function Button({ children, onClick, type = "button", disabled }: Props) {
  return (
    <button className="btn-primary" type={type} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}
```

- [ ] **Step 4: Crear `frontend/src/components/ScreenCard.tsx`**

```tsx
import type { ReactNode } from "react";

export default function ScreenCard({ children }: { children: ReactNode }) {
  return <div className="screen-card">{children}</div>;
}
```

- [ ] **Step 5: Escribir el test `frontend/src/components/Button.test.tsx`**

```tsx
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
```

- [ ] **Step 6: Ejecutar tests**

Run (desde `frontend/`): `npm test`
Expected: tests de Button PASS (3 totales con App).

- [ ] **Step 7: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): add design tokens and Button/ScreenCard primitives"
```
