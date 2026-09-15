# Task i18n: Multilenguaje (detección de navegador + selección por el usuario)

Añadir internacionalización al frontend de Chispa. Idiomas iniciales: **es** (base/fallback) y **en**.
Detectar idioma del navegador; el usuario puede cambiarlo y se persiste en `localStorage` (`chispa_lang`).
Usa el código EXACTO que aparece aquí. Trabajas en la rama `feature-entrega2-chispa`, directorio `frontend/`.

## Nuevos archivos

### Crear `frontend/src/i18n/translations.ts`

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
    "field.name": "Tu nombre",
    "field.email": "Email",
    "field.password": "Contraseña",
    "createFamily.error": "No se pudo crear la cuenta",
    "createFamily.submit": "Crear cuenta",
    "createFamily.haveAccount": "¿Ya navegas con nosotros?",
    "action.enter": "Entrar",
    "login.title": "⚓ Entrar",
    "login.error": "Email o contraseña incorrectos",
    "login.errorGeneric": "Error al entrar",
    "login.new": "¿Nuevo?",
    "addExplorer.title": "Nuevo explorador",
    "field.alias": "Alias",
    "field.birthdate": "Fecha de nacimiento",
    "field.pin": "Clave secreta (PIN)",
    "addExplorer.error": "No se pudo guardar",
    "addExplorer.submit": "Guardar explorador",
    "common.yearsOld": "años",
    "who.title": "¿Quién va a explorar?",
    "who.error": "No se pudo cargar la tripulación",
    "who.addExplorer": "＋ Añadir explorador",
    "childAccess.title": "Pon tu clave para zarpar",
    "childAccess.error": "Clave incorrecta",
  },
  en: {
    "createFamily.title": "⚓ Create your family space",
    "field.name": "Your name",
    "field.email": "Email",
    "field.password": "Password",
    "createFamily.error": "Could not create the account",
    "createFamily.submit": "Create account",
    "createFamily.haveAccount": "Already sailing with us?",
    "action.enter": "Log in",
    "login.title": "⚓ Log in",
    "login.error": "Wrong email or password",
    "login.errorGeneric": "Login error",
    "login.new": "New here?",
    "addExplorer.title": "New explorer",
    "field.alias": "Alias",
    "field.birthdate": "Date of birth",
    "field.pin": "Secret key (PIN)",
    "addExplorer.error": "Could not save",
    "addExplorer.submit": "Save explorer",
    "common.yearsOld": "years old",
    "who.title": "Who's going to explore?",
    "who.error": "Could not load the crew",
    "who.addExplorer": "＋ Add explorer",
    "childAccess.title": "Enter your key to set sail",
    "childAccess.error": "Wrong key",
  },
};
```

### Crear `frontend/src/i18n/I18nContext.tsx`

```tsx
import { createContext, useCallback, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { translations, type Lang } from "./translations";

const STORAGE_KEY = "chispa_lang";

export function detectLang(): Lang {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "es" || stored === "en") return stored;
  const nav = (navigator.language || "es").slice(0, 2).toLowerCase();
  return nav === "en" ? "en" : "es";
}

type I18n = { lang: Lang; setLang: (l: Lang) => void; t: (key: string) => string };

const I18nCtx = createContext<I18n | null>(null);

export function I18nProvider({
  children,
  initialLang,
}: {
  children: ReactNode;
  initialLang?: Lang;
}) {
  const [lang, setLangState] = useState<Lang>(initialLang ?? detectLang());

  const setLang = useCallback((l: Lang) => {
    localStorage.setItem(STORAGE_KEY, l);
    setLangState(l);
  }, []);

  const t = useCallback((key: string) => translations[lang][key] ?? key, [lang]);

  const value = useMemo(() => ({ lang, setLang, t }), [lang, setLang, t]);
  return <I18nCtx.Provider value={value}>{children}</I18nCtx.Provider>;
}

export function useI18n(): I18n {
  const ctx = useContext(I18nCtx);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
```

### Crear `frontend/src/components/LanguageSwitcher.tsx`

```tsx
import { LANGS, type Lang } from "../i18n/translations";
import { useI18n } from "../i18n/I18nContext";

export default function LanguageSwitcher() {
  const { lang, setLang } = useI18n();
  return (
    <label
      style={{ display: "flex", gap: 6, alignItems: "center", fontSize: 13, alignSelf: "flex-end" }}
    >
      🌐
      <select
        aria-label="Idioma / Language"
        value={lang}
        onChange={(e) => setLang(e.target.value as Lang)}
        style={{ borderRadius: 10, padding: "4px 8px", fontFamily: "var(--font-body)" }}
      >
        {LANGS.map((l) => (
          <option key={l.code} value={l.code}>
            {l.label}
          </option>
        ))}
      </select>
    </label>
  );
}
```

### Crear el test `frontend/src/i18n/I18nContext.test.tsx`

```tsx
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
```

## Cablear el provider en `frontend/src/main.tsx` (contenido completo)

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./styles/theme.css";
import App from "./App";
import { SessionProvider } from "./auth/SessionContext";
import { I18nProvider } from "./i18n/I18nContext";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <I18nProvider>
      <SessionProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </SessionProvider>
    </I18nProvider>
  </StrictMode>,
);
```

## Refactor de pantallas para usar `t()` (reemplaza el contenido completo de cada archivo)

### `frontend/src/screens/CreateFamily.tsx`

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
      <h1>{t("createFamily.title")}</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
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
        {error && <p role="alert" style={{ color: "#b23" }}>{error}</p>}
        <Button type="submit" disabled={busy}>
          {t("createFamily.submit")}
        </Button>
      </form>
      <p style={{ textAlign: "center" }}>
        {t("createFamily.haveAccount")} <Link to="/login">{t("action.enter")}</Link>
      </p>
    </ScreenCard>
  );
}
```

### `frontend/src/screens/Login.tsx`

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
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
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
        {error && <p role="alert" style={{ color: "#b23" }}>{error}</p>}
        <Button type="submit" disabled={busy}>
          {t("action.enter")}
        </Button>
      </form>
      <p style={{ textAlign: "center" }}>
        {t("login.new")} <Link to="/">{t("createFamily.submit")}</Link>
      </p>
    </ScreenCard>
  );
}
```

### `frontend/src/screens/AddExplorer.tsx`

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
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const { t } = useI18n();
  const age = ageFrom(birthdate);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
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

  return (
    <ScreenCard>
      <h1>{t("addExplorer.title")}</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
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
          <div aria-label="edad calculada">
            {age} {t("common.yearsOld")}
          </div>
        )}
        <label>
          {t("field.pin")}
          <input
            inputMode="numeric"
            pattern="[0-9]*"
            minLength={4}
            maxLength={8}
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            required
          />
        </label>
        {error && <p role="alert">{error}</p>}
        <Button type="submit" disabled={busy}>
          {t("addExplorer.submit")}
        </Button>
      </form>
    </ScreenCard>
  );
}
```

### `frontend/src/screens/WhoExplores.tsx`

```tsx
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { listChildren, type Child } from "../api/children";
import { useI18n } from "../i18n/I18nContext";
import ScreenCard from "../components/ScreenCard";

export default function WhoExplores() {
  const [children, setChildren] = useState<Child[]>([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { t } = useI18n();

  useEffect(() => {
    listChildren()
      .then(setChildren)
      .catch(() => setError(t("who.error")));
  }, [t]);

  return (
    <ScreenCard>
      <h1>{t("who.title")}</h1>
      {error && <p role="alert">{error}</p>}
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {children.map((c) => (
          <button
            key={c.id}
            onClick={() => navigate(`/explorar/${c.id}`)}
            style={{ textAlign: "left", padding: 16 }}
          >
            <strong>{c.name}</strong>
            <div>
              {c.age} {t("common.yearsOld")}
            </div>
          </button>
        ))}
        <Link to="/familia/nuevo">{t("who.addExplorer")}</Link>
      </div>
    </ScreenCard>
  );
}
```

### `frontend/src/screens/ChildAccess.tsx`

```tsx
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { childLogin } from "../api/children";
import { setToken } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import ScreenCard from "../components/ScreenCard";

export default function ChildAccess() {
  const { childId } = useParams();
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const { t } = useI18n();

  useEffect(() => {
    if (pin.length === 4 && childId) {
      childLogin(Number(childId), pin)
        .then((res) => setToken(res.access_token))
        .catch(() => {
          setError(t("childAccess.error"));
          setPin("");
        });
    }
  }, [pin, childId, t]);

  const keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "⌫"];

  return (
    <ScreenCard>
      <h1>{t("childAccess.title")}</h1>
      <div aria-label="pin" style={{ display: "flex", gap: 14, justifyContent: "center" }}>
        {[0, 1, 2, 3].map((i) => (
          <span
            key={i}
            style={{
              width: 14,
              height: 14,
              borderRadius: 99,
              background: i < pin.length ? "var(--coral)" : "rgba(255,255,255,.5)",
            }}
          />
        ))}
      </div>
      {error && <p role="alert">{error}</p>}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 14, marginTop: 20 }}>
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

## Actualizar los tests existentes para envolver en `I18nProvider initialLang="es"`

Los tests existentes comprueban texto en español, así que deben renderizar dentro de un
`<I18nProvider initialLang="es">`. Modifica SOLO el render (añade el wrapper más externo), sin cambiar las aserciones:

- `frontend/src/screens/CreateFamily.test.tsx`: en `setup()`, envuelve con `<I18nProvider initialLang="es">` por fuera de `<SessionProvider>`. Añade el import `import { I18nProvider } from "../i18n/I18nContext";`.
- `frontend/src/screens/WhoExplores.test.tsx`: envuelve `<MemoryRouter>` con `<I18nProvider initialLang="es">`. Import correspondiente.
- `frontend/src/screens/ChildAccess.test.tsx`: envuelve `<MemoryRouter ...>` con `<I18nProvider initialLang="es">`. Import correspondiente.
- `frontend/src/App.test.tsx`: envuelve con `<I18nProvider initialLang="es">` por fuera de `<SessionProvider>`. Import correspondiente.

Ejemplo (CreateFamily.test.tsx `setup`):

```tsx
import { I18nProvider } from "../i18n/I18nContext";
// ...
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
```

## Verificación, lint y commit

- [ ] Run (desde `frontend/`): `npm test` → todos PASS (incluido el nuevo `I18nContext.test.tsx`).
- [ ] Run (desde `frontend/`): `npm run lint` → sin errores TypeScript.
- [ ] Commit:

```bash
git add frontend/
git commit -m "feat(frontend): i18n (browser detection + language switcher, es/en)"
```
