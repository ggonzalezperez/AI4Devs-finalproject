# Task PWD-b: Cambiar y recuperar contraseña (frontend)

Frontend `frontend/`. Rama `feature-password`. SIN push.
PWD-a (backend) ya expone: `POST /auth/register` → `{access_token, recovery_code}`; `POST /auth/change-password` (auth familia) `{current_password, new_password}`; `POST /auth/reset-password` `{email, recovery_code, new_password}` → `{recovery_code}` (nuevo, rotado).

Flujos: (1) al registrarse se muestra el **código de recuperación** para guardar; (2) pantalla **cambiar contraseña** (logueado); (3) pantalla **recuperar** (email + código + nueva).

**Files:**
- Modify: `frontend/src/api/auth.ts` (tipos + changePassword + resetPassword)
- Modify: `frontend/src/screens/CreateFamily.tsx` (mostrar código tras registro)
- Modify: `frontend/src/screens/Login.tsx` (enlace "¿Olvidaste tu contraseña?")
- Create: `frontend/src/screens/ChangePassword.tsx` + ruta `/familia/password`
- Create: `frontend/src/screens/ResetPassword.tsx` + ruta `/recuperar`
- Modify: `frontend/src/screens/WhoExplores.tsx` (enlace a cambiar contraseña)
- Modify: `frontend/src/App.tsx` (rutas)
- Modify: `frontend/src/i18n/translations.ts` (claves `pwd.*`)
- Tests

## Step 1: `frontend/src/api/auth.ts`
Lee el archivo. Ajusta el tipo/función de registro para incluir `recovery_code` y añade las dos funciones nuevas. `registerFamily` debe devolver `{ access_token: string; recovery_code: string }` (mantén compatibilidad: si hoy devuelve `TokenResponse`, crea `RegisterResult = TokenResponse & { recovery_code: string }` y tipa el retorno con eso).
```ts
export function changePassword(currentPassword: string, newPassword: string) {
  return apiFetch<{ status: string }>("/auth/change-password", {
    method: "POST",
    auth: true,
    body: { current_password: currentPassword, new_password: newPassword },
  });
}

export function resetPassword(email: string, recoveryCode: string, newPassword: string) {
  return apiFetch<{ recovery_code: string }>("/auth/reset-password", {
    method: "POST",
    body: { email, recovery_code: recoveryCode, new_password: newPassword },
  });
}
```

## Step 2: i18n — `frontend/src/i18n/translations.ts` (es + en)
es:
```
    "pwd.recoveryTitle": "Guarda tu código de recuperación",
    "pwd.recoverySubtitle": "Si olvidas tu contraseña, lo necesitarás para recuperar la cuenta. Guárdalo en un lugar seguro.",
    "pwd.copy": "Copiar código",
    "pwd.copied": "¡Copiado!",
    "pwd.continue": "Continuar",
    "pwd.forgot": "¿Olvidaste tu contraseña?",
    "pwd.changeTitle": "🔑 Cambiar contraseña",
    "pwd.current": "Contraseña actual",
    "pwd.new": "Nueva contraseña",
    "pwd.confirm": "Repite la nueva contraseña",
    "pwd.save": "Cambiar contraseña",
    "pwd.changed": "Contraseña cambiada ✓",
    "pwd.currentWrong": "La contraseña actual no es correcta",
    "pwd.mismatch": "Las contraseñas no coinciden",
    "pwd.changeLink": "🔑 Cambiar contraseña",
    "pwd.resetTitle": "Recuperar contraseña",
    "pwd.resetSubtitle": "Introduce tu email, tu código de recuperación y una contraseña nueva.",
    "pwd.recoveryCode": "Código de recuperación",
    "pwd.resetSubmit": "Restablecer contraseña",
    "pwd.resetError": "Email o código de recuperación incorrectos",
    "pwd.resetDone": "¡Contraseña restablecida! Guarda tu NUEVO código de recuperación:",
    "pwd.toLogin": "Ir a entrar",
```
en:
```
    "pwd.recoveryTitle": "Save your recovery code",
    "pwd.recoverySubtitle": "If you forget your password, you'll need it to recover the account. Keep it somewhere safe.",
    "pwd.copy": "Copy code",
    "pwd.copied": "Copied!",
    "pwd.continue": "Continue",
    "pwd.forgot": "Forgot your password?",
    "pwd.changeTitle": "🔑 Change password",
    "pwd.current": "Current password",
    "pwd.new": "New password",
    "pwd.confirm": "Repeat the new password",
    "pwd.save": "Change password",
    "pwd.changed": "Password changed ✓",
    "pwd.currentWrong": "The current password is incorrect",
    "pwd.mismatch": "Passwords do not match",
    "pwd.changeLink": "🔑 Change password",
    "pwd.resetTitle": "Recover password",
    "pwd.resetSubtitle": "Enter your email, your recovery code and a new password.",
    "pwd.recoveryCode": "Recovery code",
    "pwd.resetSubmit": "Reset password",
    "pwd.resetError": "Wrong email or recovery code",
    "pwd.resetDone": "Password reset! Save your NEW recovery code:",
    "pwd.toLogin": "Go to sign in",
```

## Step 3: `frontend/src/screens/CreateFamily.tsx` — mostrar código tras registro
Lee el archivo. Tiene el guard `if (isAuthenticated) return <Navigate to="/familia" />`, y en `handleSubmit` hace `login(access_token); navigate("/familia")`. Cámbialo para que, tras el registro, muestre PRIMERO el código de recuperación y NO llame a `login()` todavía (si no, el guard redirige y no se ve el código):
- Añade estado: `const [pending, setPending] = useState<{ token: string; code: string } | null>(null);`
- En el `try` del registro, en vez de `login(...)`+`navigate(...)`, haz:
```tsx
      const { access_token, recovery_code } = await registerFamily(name, email, password);
      setPending({ token: access_token, code: recovery_code });
```
- Al principio del `return` (antes del formulario), si hay `pending`, renderiza el panel del código:
```tsx
  if (pending) {
    return (
      <ScreenCard>
        <LanguageSwitcher />
        <h1>{t("pwd.recoveryTitle")}</h1>
        <p style={{ color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>{t("pwd.recoverySubtitle")}</p>
        <div style={{ background: "#fff", borderRadius: 16, padding: 18, textAlign: "center" }}>
          <code style={{ fontSize: 18, fontWeight: 800, color: "var(--teal-dark)", wordBreak: "break-all" }}>
            {pending.code}
          </code>
        </div>
        <button onClick={() => { void navigator.clipboard?.writeText(pending.code); }}>{t("pwd.copy")}</button>
        <Button onClick={() => { login(pending.token); navigate("/familia"); }}>{t("pwd.continue")}</Button>
      </ScreenCard>
    );
  }
```
(El guard `isAuthenticated` sigue arriba; como no llamamos `login()` hasta "Continuar", no redirige.)

## Step 4: `frontend/src/screens/Login.tsx`
Añade bajo el formulario un enlace a recuperar:
```tsx
      <p style={{ textAlign: "center", fontSize: 13 }}>
        <Link to="/recuperar">{t("pwd.forgot")}</Link>
      </p>
```

## Step 5: `frontend/src/screens/ChangePassword.tsx` (nueva)
```tsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { changePassword } from "../api/auth";
import { ApiError } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

export default function ChangePassword() {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (next.length < 8) { setError(t("validation.passwordShort")); return; }
    if (next !== confirm) { setError(t("pwd.mismatch")); return; }
    setBusy(true);
    try {
      await changePassword(current, next);
      setDone(true);
      setTimeout(() => navigate("/familia"), 1200);
    } catch (err) {
      setError(err instanceof ApiError && err.status === 400 ? t("pwd.currentWrong") : t("createFamily.error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <Link to="/familia/explorar">←</Link>
      <h1>{t("pwd.changeTitle")}</h1>
      <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 20, padding: 18 }}>
        <label>{t("pwd.current")}<input type="password" value={current} onChange={(e) => setCurrent(e.target.value)} required /></label>
        <label>{t("pwd.new")}<input type="password" value={next} onChange={(e) => setNext(e.target.value)} required /></label>
        <label>{t("pwd.confirm")}<input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required /></label>
        {error && <p role="alert" style={{ color: "#c0392b", fontWeight: 700, margin: 0 }}>{error}</p>}
        {done && <p style={{ color: "var(--green)", fontWeight: 700, margin: 0 }}>{t("pwd.changed")}</p>}
        <Button type="submit" disabled={busy}>{t("pwd.save")}</Button>
      </form>
    </ScreenCard>
  );
}
```

## Step 6: `frontend/src/screens/ResetPassword.tsx` (nueva)
```tsx
import { useState } from "react";
import { Link } from "react-router-dom";
import { resetPassword } from "../api/auth";
import { ApiError } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";
import LanguageSwitcher from "../components/LanguageSwitcher";

export default function ResetPassword() {
  const { t } = useI18n();
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [newCode, setNewCode] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (next.length < 8) { setError(t("validation.passwordShort")); return; }
    if (next !== confirm) { setError(t("pwd.mismatch")); return; }
    setBusy(true);
    try {
      const res = await resetPassword(email.trim(), code.trim(), next);
      setNewCode(res.recovery_code);
    } catch (err) {
      setError(err instanceof ApiError ? t("pwd.resetError") : t("createFamily.error"));
    } finally {
      setBusy(false);
    }
  }

  if (newCode) {
    return (
      <ScreenCard>
        <LanguageSwitcher />
        <h1>{t("pwd.resetTitle")}</h1>
        <p style={{ color: "#0a5a53", fontWeight: 700 }}>{t("pwd.resetDone")}</p>
        <div style={{ background: "#fff", borderRadius: 16, padding: 18, textAlign: "center" }}>
          <code style={{ fontSize: 18, fontWeight: 800, color: "var(--teal-dark)", wordBreak: "break-all" }}>{newCode}</code>
        </div>
        <Link to="/login" style={{ textAlign: "center" }}>{t("pwd.toLogin")}</Link>
      </ScreenCard>
    );
  }

  return (
    <ScreenCard>
      <LanguageSwitcher />
      <h1>{t("pwd.resetTitle")}</h1>
      <p style={{ color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>{t("pwd.resetSubtitle")}</p>
      <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 20, padding: 18 }}>
        <label>{t("field.email")}<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
        <label>{t("pwd.recoveryCode")}<input value={code} onChange={(e) => setCode(e.target.value)} required placeholder="XXXX-XXXX-…" /></label>
        <label>{t("pwd.new")}<input type="password" value={next} onChange={(e) => setNext(e.target.value)} required /></label>
        <label>{t("pwd.confirm")}<input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required /></label>
        {error && <p role="alert" style={{ color: "#c0392b", fontWeight: 700, margin: 0 }}>{error}</p>}
        <Button type="submit" disabled={busy}>{t("pwd.resetSubmit")}</Button>
      </form>
      <Link to="/login" style={{ textAlign: "center", fontSize: 13 }}>{t("pwd.toLogin")}</Link>
    </ScreenCard>
  );
}
```

## Step 7: `frontend/src/App.tsx`
Importa las dos pantallas. Añade la pública fuera de `ProtectedRoute` (junto a `/login`):
```tsx
      <Route path="/recuperar" element={<ResetPassword />} />
```
y la protegida dentro de `<ProtectedRoute />`:
```tsx
        <Route path="/familia/password" element={<ChangePassword />} />
```

## Step 8: `frontend/src/screens/WhoExplores.tsx`
Junto a los enlaces del pie, añade: `<Link to="/familia/password" style={{ textAlign: "center", marginTop: 4 }}>{t("pwd.changeLink")}</Link>`

## Step 9: Tests
- `CreateFamily.test.tsx`: el mock de `/auth/register` debe devolver `recovery_code` (p. ej. `"AAAA-BBBB-CCCC-DDDD-EEEE-FFFF-0000-1111"`). El flujo cambió: tras enviar el registro se muestra el **código de recuperación** (no navega directo). Ajusta la aserción "submits registration and stores token": ahora comprueba que aparece el código (`getByText` del código o de `pwd.recoveryTitle`) y que al pulsar **Continuar** se guarda el token (`localStorage.getItem("chispa_token")`). Mantén verdes los tests de error (passwords no coinciden, email existe).
- Añade `ChangePassword.test.tsx` (opcional) y/o `ResetPassword.test.tsx`: un test simple de que renderiza sus campos.
- Ejecuta `npm test` y `npm run lint` → verde/limpio. Arregla cualquier test que rompa por el cambio de shape de `registerFamily`.

## Step 10: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): change-password screen + forgot-password recovery flow"
```
