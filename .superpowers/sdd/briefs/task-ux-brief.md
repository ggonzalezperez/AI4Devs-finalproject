# Task UX: Arreglo del PIN + confirmaciones + pulido UX/UI (Archipiélago)

Objetivos:
1. **PIN de exactamente 4 dígitos** en todo el flujo (arregla el fallo de "clave incorrecta").
2. **Confirmación de contraseña** en el alta de familia y **confirmación de PIN** al crear explorador, con validación y mensajes claros.
3. **Pulido UX/UI** acorde al diseño "Archipiélago": subtítulos, avatares derivados, estados de éxito y vacío, mensajes de validación, responsive.

Usa el código EXACTO de abajo (reemplaza el contenido completo de cada archivo). Rama: `feature-entrega2-chispa`, dir `frontend/`.
Las clases CSS ya dan estilo a `input` y `button` dentro de `.screen-card` (no añadas CSS).

## Nuevo: `frontend/src/lib/avatar.ts`

```ts
const AVATARS = ["🦊", "🐢", "🦉", "🐬", "🦁", "🐼", "🦄", "🐙"];

export function avatarFor(id: number): string {
  return AVATARS[((id % AVATARS.length) + AVATARS.length) % AVATARS.length];
}
```

## Reemplazar `frontend/src/i18n/translations.ts` (añade claves nuevas; es base, en espejo)

```ts
export type Lang = "es" | "en";

export const LANGS: { code: Lang; label: string }[] = [
  { code: "es", label: "Español" },
  { code: "en", label: "English" },
];

type Dict = Record<string, string>;

export const translations: Record<Lang, Dict> = {
  es: {
    "createFamily.title": "⚓ Crea el espacio de tu familia",
    "createFamily.subtitle": "Tú administras. Tus hijos exploran, seguros.",
    "createFamily.safety": "Sin datos del menor. Solo tú administras la tripulación.",
    "field.name": "Tu nombre",
    "field.email": "Email",
    "field.password": "Contraseña",
    "field.passwordConfirm": "Repite la contraseña",
    "createFamily.error": "No se pudo crear la cuenta",
    "createFamily.submit": "Crear cuenta",
    "createFamily.haveAccount": "¿Ya navegas con nosotros?",
    "action.enter": "Entrar",
    "login.title": "⚓ Entrar",
    "login.error": "Email o contraseña incorrectos",
    "login.errorGeneric": "Error al entrar",
    "login.new": "¿Nuevo?",
    "addExplorer.title": "Nuevo explorador",
    "addExplorer.subtitle": "Un alias, su fecha de nacimiento y una clave de 4 dígitos.",
    "field.alias": "Alias",
    "field.birthdate": "Fecha de nacimiento",
    "field.pin": "Clave de 4 dígitos (PIN)",
    "field.pinConfirm": "Repite la clave",
    "addExplorer.error": "No se pudo guardar",
    "addExplorer.submit": "Guardar explorador",
    "common.yearsOld": "años",
    "who.title": "¿Quién va a explorar?",
    "who.subtitle": "Elige tu perfil para zarpar.",
    "who.empty": "Aún no hay exploradores. ¡Añade el primero!",
    "who.error": "No se pudo cargar la tripulación",
    "who.addExplorer": "＋ Añadir explorador",
    "childAccess.hello": "¡Hola, {name}!",
    "childAccess.title": "Pon tu clave para zarpar",
    "childAccess.error": "Clave incorrecta",
    "childAccess.success": "¡Listo! A explorar 🎉",
    "validation.passwordShort": "La contraseña debe tener al menos 8 caracteres",
    "validation.passwordMismatch": "Las contraseñas no coinciden",
    "validation.pinLength": "El PIN debe tener 4 dígitos",
    "validation.pinMismatch": "Las claves no coinciden",
  },
  en: {
    "createFamily.title": "⚓ Create your family space",
    "createFamily.subtitle": "You manage it. Your kids explore, safely.",
    "createFamily.safety": "No child data. Only you manage the crew.",
    "field.name": "Your name",
    "field.email": "Email",
    "field.password": "Password",
    "field.passwordConfirm": "Repeat password",
    "createFamily.error": "Could not create the account",
    "createFamily.submit": "Create account",
    "createFamily.haveAccount": "Already sailing with us?",
    "action.enter": "Log in",
    "login.title": "⚓ Log in",
    "login.error": "Wrong email or password",
    "login.errorGeneric": "Login error",
    "login.new": "New here?",
    "addExplorer.title": "New explorer",
    "addExplorer.subtitle": "An alias, their date of birth and a 4-digit key.",
    "field.alias": "Alias",
    "field.birthdate": "Date of birth",
    "field.pin": "4-digit key (PIN)",
    "field.pinConfirm": "Repeat the key",
    "addExplorer.error": "Could not save",
    "addExplorer.submit": "Save explorer",
    "common.yearsOld": "years old",
    "who.title": "Who's going to explore?",
    "who.subtitle": "Pick your profile to set sail.",
    "who.empty": "No explorers yet. Add the first one!",
    "who.error": "Could not load the crew",
    "who.addExplorer": "＋ Add explorer",
    "childAccess.hello": "Hi, {name}!",
    "childAccess.title": "Enter your key to set sail",
    "childAccess.error": "Wrong key",
    "childAccess.success": "Done! Let's explore 🎉",
    "validation.passwordShort": "Password must be at least 8 characters",
    "validation.passwordMismatch": "Passwords do not match",
    "validation.pinLength": "The PIN must be 4 digits",
    "validation.pinMismatch": "The keys do not match",
  },
};
```

## Reemplazar `frontend/src/screens/CreateFamily.tsx`

```tsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerFamily } from "../api/auth";
import { ApiError } from "../api/client";
import { useSession } from "../auth/SessionContext";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";
import LanguageSwitcher from "../components/LanguageSwitcher";

export default function CreateFamily() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { login } = useSession();
  const { t } = useI18n();
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (password.length < 8) {
      setError(t("validation.passwordShort"));
      return;
    }
    if (password !== confirm) {
      setError(t("validation.passwordMismatch"));
      return;
    }
    setBusy(true);
    try {
      const { access_token } = await registerFamily(name, email, password);
      login(access_token);
      navigate("/familia");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("createFamily.error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <LanguageSwitcher />
      <div>
        <h1>{t("createFamily.title")}</h1>
        <p style={{ margin: "4px 0 0", color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>
          {t("createFamily.subtitle")}
        </p>
      </div>
      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 20, padding: 18 }}
      >
        <label>
          {t("field.name")}
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          {t("field.email")}
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          {t("field.password")}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        <label>
          {t("field.passwordConfirm")}
          <input
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
          />
        </label>
        {error && (
          <p role="alert" style={{ color: "#c0392b", margin: 0, fontWeight: 700, fontSize: 14 }}>
            {error}
          </p>
        )}
        <Button type="submit" disabled={busy}>
          {t("createFamily.submit")}
        </Button>
      </form>
      <p style={{ textAlign: "center", fontSize: 13 }}>
        {t("createFamily.haveAccount")} <Link to="/login">{t("action.enter")}</Link>
      </p>
      <div
        style={{ marginTop: "auto", display: "flex", gap: 8, alignItems: "center", background: "rgba(255,255,255,.55)", borderRadius: 12, padding: "10px 12px", fontSize: 12, color: "#0a5a53" }}
      >
        🔒 {t("createFamily.safety")}
      </div>
    </ScreenCard>
  );
}
```

## Reemplazar `frontend/src/screens/Login.tsx`

```tsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginFamily } from "../api/auth";
import { ApiError } from "../api/client";
import { useSession } from "../auth/SessionContext";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";
import LanguageSwitcher from "../components/LanguageSwitcher";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { login } = useSession();
  const { t } = useI18n();
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { access_token } = await loginFamily(email, password);
      login(access_token);
      navigate("/familia");
    } catch (err) {
      setError(err instanceof ApiError ? t("login.error") : t("login.errorGeneric"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <LanguageSwitcher />
      <h1>{t("login.title")}</h1>
      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 20, padding: 18 }}
      >
        <label>
          {t("field.email")}
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          {t("field.password")}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && (
          <p role="alert" style={{ color: "#c0392b", margin: 0, fontWeight: 700, fontSize: 14 }}>
            {error}
          </p>
        )}
        <Button type="submit" disabled={busy}>
          {t("action.enter")}
        </Button>
      </form>
      <p style={{ textAlign: "center", fontSize: 13 }}>
        {t("login.new")} <Link to="/">{t("createFamily.submit")}</Link>
      </p>
    </ScreenCard>
  );
}
```

## Reemplazar `frontend/src/screens/AddExplorer.tsx`

```tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createChild } from "../api/children";
import { ApiError } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

function ageFrom(birthdate: string): number | null {
  if (!birthdate) return null;
  const b = new Date(birthdate);
  const t = new Date();
  let age = t.getFullYear() - b.getFullYear();
  const m = t.getMonth() - b.getMonth();
  if (m < 0 || (m === 0 && t.getDate() < b.getDate())) age--;
  return age;
}

export default function AddExplorer() {
  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [pin, setPin] = useState("");
  const [pinConfirm, setPinConfirm] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const { t } = useI18n();
  const age = ageFrom(birthdate);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!/^\d{4}$/.test(pin)) {
      setError(t("validation.pinLength"));
      return;
    }
    if (pin !== pinConfirm) {
      setError(t("validation.pinMismatch"));
      return;
    }
    setBusy(true);
    try {
      await createChild(name, birthdate, pin);
      navigate("/familia/explorar");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("addExplorer.error"));
    } finally {
      setBusy(false);
    }
  }

  const pinInputStyle = { letterSpacing: "0.5em", textAlign: "center" as const };

  return (
    <ScreenCard>
      <div>
        <h1>{t("addExplorer.title")}</h1>
        <p style={{ margin: "4px 0 0", color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>
          {t("addExplorer.subtitle")}
        </p>
      </div>
      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 20, padding: 18 }}
      >
        <label>
          {t("field.alias")}
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          {t("field.birthdate")}
          <input
            type="date"
            value={birthdate}
            onChange={(e) => setBirthdate(e.target.value)}
            required
          />
        </label>
        {age !== null && (
          <div
            aria-label="edad calculada"
            style={{ alignSelf: "flex-start", background: "#e6f7ee", color: "#2aa06a", fontWeight: 800, padding: "6px 12px", borderRadius: 12 }}
          >
            {age} {t("common.yearsOld")}
          </div>
        )}
        <label>
          {t("field.pin")}
          <input
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={4}
            value={pin}
            onChange={(e) => setPin(e.target.value.replace(/\D/g, ""))}
            style={pinInputStyle}
            required
          />
        </label>
        <label>
          {t("field.pinConfirm")}
          <input
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={4}
            value={pinConfirm}
            onChange={(e) => setPinConfirm(e.target.value.replace(/\D/g, ""))}
            style={pinInputStyle}
            required
          />
        </label>
        {error && (
          <p role="alert" style={{ color: "#c0392b", margin: 0, fontWeight: 700, fontSize: 14 }}>
            {error}
          </p>
        )}
        <Button type="submit" disabled={busy}>
          {t("addExplorer.submit")}
        </Button>
      </form>
    </ScreenCard>
  );
}
```

## Reemplazar `frontend/src/screens/WhoExplores.tsx`

```tsx
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { listChildren, type Child } from "../api/children";
import { useI18n } from "../i18n/I18nContext";
import { avatarFor } from "../lib/avatar";
import ScreenCard from "../components/ScreenCard";

export default function WhoExplores() {
  const [children, setChildren] = useState<Child[]>([]);
  const [error, setError] = useState("");
  const [loaded, setLoaded] = useState(false);
  const navigate = useNavigate();
  const { t } = useI18n();

  useEffect(() => {
    listChildren()
      .then(setChildren)
      .catch(() => setError(t("who.error")))
      .finally(() => setLoaded(true));
  }, [t]);

  return (
    <ScreenCard>
      <div>
        <h1>{t("who.title")}</h1>
        <p style={{ margin: "4px 0 0", color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>
          {t("who.subtitle")}
        </p>
      </div>
      {error && <p role="alert">{error}</p>}
      {loaded && children.length === 0 && !error && (
        <p style={{ color: "#0a5a53", fontWeight: 600 }}>{t("who.empty")}</p>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {children.map((c) => (
          <button
            key={c.id}
            onClick={() => navigate(`/explorar/${c.id}`, { state: { name: c.name } })}
            style={{ display: "flex", alignItems: "center", gap: 14, textAlign: "left", padding: 16 }}
          >
            <span style={{ fontSize: 30 }}>{avatarFor(c.id)}</span>
            <span style={{ flex: 1 }}>
              <strong style={{ display: "block", fontSize: 18 }}>{c.name}</strong>
              <span style={{ fontSize: 13, color: "#0a5a53" }}>
                {c.age} {t("common.yearsOld")}
              </span>
            </span>
            <span style={{ color: "var(--coral)", fontSize: 22 }}>→</span>
          </button>
        ))}
      </div>
      <Link to="/familia/nuevo" style={{ textAlign: "center", marginTop: 4 }}>
        {t("who.addExplorer")}
      </Link>
    </ScreenCard>
  );
}
```

## Reemplazar `frontend/src/screens/ChildAccess.tsx`

```tsx
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { childLogin } from "../api/children";
import { setToken } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import { avatarFor } from "../lib/avatar";
import ScreenCard from "../components/ScreenCard";

export default function ChildAccess() {
  const { childId } = useParams();
  const location = useLocation();
  const name = (location.state as { name?: string } | null)?.name;
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const { t } = useI18n();

  useEffect(() => {
    if (pin.length === 4 && childId) {
      childLogin(Number(childId), pin)
        .then((res) => {
          setToken(res.access_token);
          setDone(true);
        })
        .catch(() => {
          setError(t("childAccess.error"));
          setPin("");
        });
    }
  }, [pin, childId, t]);

  if (done) {
    return (
      <ScreenCard>
        <div style={{ margin: "auto", textAlign: "center" }}>
          <div style={{ fontSize: 64 }}>🎉</div>
          <h1>{t("childAccess.success")}</h1>
        </div>
      </ScreenCard>
    );
  }

  const keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "⌫"];

  return (
    <ScreenCard>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: 52 }}>{avatarFor(Number(childId))}</div>
        {name && (
          <div style={{ fontFamily: "var(--font-head)", fontSize: 24, color: "var(--teal-dark)" }}>
            {t("childAccess.hello").replace("{name}", name)}
          </div>
        )}
        <div style={{ color: "#0a5a53", fontWeight: 600, marginTop: 2 }}>{t("childAccess.title")}</div>
      </div>
      <div aria-label="pin" style={{ display: "flex", gap: 14, justifyContent: "center", marginTop: 6 }}>
        {[0, 1, 2, 3].map((i) => (
          <span
            key={i}
            style={{
              width: 16,
              height: 16,
              borderRadius: 99,
              background: i < pin.length ? "var(--coral)" : "rgba(255,255,255,.5)",
            }}
          />
        ))}
      </div>
      {error && <p role="alert" style={{ textAlign: "center", color: "#fff", fontWeight: 700 }}>{error}</p>}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 14, marginTop: 14 }}>
        {keys.map((k, idx) =>
          k === "" ? (
            <div key={idx} />
          ) : (
            <button
              key={idx}
              onClick={() =>
                k === "⌫" ? setPin((p) => p.slice(0, -1)) : setPin((p) => (p + k).slice(0, 4))
              }
            >
              {k}
            </button>
          ),
        )}
      </div>
    </ScreenCard>
  );
}
```

## Reemplazar el test `frontend/src/screens/CreateFamily.test.tsx`

(Ahora hay dos campos de contraseña; usa etiquetas exactas y rellena la confirmación.)

```tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import { SessionProvider } from "../auth/SessionContext";
import CreateFamily from "./CreateFamily";

beforeEach(() => localStorage.clear());
afterEach(() => vi.restoreAllMocks());

function setup() {
  render(
    <I18nProvider initialLang="es">
      <SessionProvider>
        <MemoryRouter>
          <CreateFamily />
        </MemoryRouter>
      </SessionProvider>
    </I18nProvider>,
  );
}

async function fillForm() {
  await userEvent.type(screen.getByLabelText("Tu nombre"), "Ana");
  await userEvent.type(screen.getByLabelText("Email"), "ana@x.com");
  await userEvent.type(screen.getByLabelText("Contraseña"), "secret123");
  await userEvent.type(screen.getByLabelText("Repite la contraseña"), "secret123");
}

test("submits registration and stores token", async () => {
  const fetchMock = vi.fn(
    async () =>
      new Response(JSON.stringify({ access_token: "t1", token_type: "bearer" }), { status: 201 }),
  );
  vi.stubGlobal("fetch", fetchMock);
  setup();
  await fillForm();
  await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
  await waitFor(() => expect(localStorage.getItem("chispa_token")).toBe("t1"));
});

test("shows error when passwords do not match", async () => {
  setup();
  await userEvent.type(screen.getByLabelText("Tu nombre"), "Ana");
  await userEvent.type(screen.getByLabelText("Email"), "ana@x.com");
  await userEvent.type(screen.getByLabelText("Contraseña"), "secret123");
  await userEvent.type(screen.getByLabelText("Repite la contraseña"), "different1");
  await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
  expect(await screen.findByText(/no coinciden/i)).toBeInTheDocument();
});

test("shows error message when email already exists", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(JSON.stringify({ detail: "Email ya registrado" }), { status: 409 }),
    ),
  );
  setup();
  await fillForm();
  await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
  expect(await screen.findByText(/email ya registrado/i)).toBeInTheDocument();
});
```

## Nuevo test `frontend/src/screens/AddExplorer.test.tsx`

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, expect, test } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import AddExplorer from "./AddExplorer";

beforeEach(() => localStorage.clear());

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
```

## Verificación, lint y commit

- [ ] Run (desde `frontend/`): `npm test` → todos PASS (incluye el nuevo AddExplorer.test).
- [ ] Run (desde `frontend/`): `npm run lint` → sin errores.
- [ ] Commit:

```bash
git add frontend/
git commit -m "feat(frontend): 4-digit PIN with confirm, password confirmation, Archipielago UX polish"
```
