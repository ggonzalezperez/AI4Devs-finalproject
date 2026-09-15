# Task QR: Conectar móvil dentro de la app (QR + URL)

Frontend `frontend/`. Rama `feature-infra-lan`. SIN push.
Pantalla en la zona de familia que muestra la **URL** de la app y un **QR** para abrirla en otro dispositivo de la misma WiFi (móvil/tablet). Usa la URL real con la que el padre está accediendo (`window.location.origin`).

Dep nueva permitida: `qrcode.react` (componente React de QR, render local, sin servicios externos).

**Files:**
- Add dep: `qrcode.react` (`npm install qrcode.react` en `frontend/`)
- Create: `frontend/src/screens/ConnectDevice.tsx`
- Modify: `frontend/src/App.tsx` (ruta `/familia/conectar` dentro de `ProtectedRoute`)
- Modify: `frontend/src/screens/WhoExplores.tsx` (enlace)
- Modify: `frontend/src/i18n/translations.ts` (claves `connect.*`)
- Test: `frontend/src/screens/ConnectDevice.test.tsx`

## Step 1: Instalar dependencia
En `frontend/`: `npm install qrcode.react`

## Step 2: i18n — `frontend/src/i18n/translations.ts`
es:
```
    "connect.title": "📱 Conectar otro dispositivo",
    "connect.subtitle": "Abre esta dirección en un móvil o tablet conectados a la misma WiFi.",
    "connect.copy": "Copiar dirección",
    "connect.copied": "¡Copiada!",
    "connect.localhostWarn": "Estás en «localhost». Para usarlo desde otro dispositivo, abre la app en este PC con su IP de red (p. ej. http://192.168.1.50:5173) y vuelve aquí.",
    "connect.link": "📱 Conectar móvil",
```
en:
```
    "connect.title": "📱 Connect another device",
    "connect.subtitle": "Open this address on a phone or tablet on the same WiFi.",
    "connect.copy": "Copy address",
    "connect.copied": "Copied!",
    "connect.localhostWarn": "You're on “localhost”. To use it from another device, open the app on this PC via its network IP (e.g. http://192.168.1.50:5173) and come back here.",
    "connect.link": "📱 Connect phone",
```

## Step 3: `frontend/src/screens/ConnectDevice.tsx`
```tsx
import { useState } from "react";
import { Link } from "react-router-dom";
import { QRCodeSVG } from "qrcode.react";
import { useI18n } from "../i18n/I18nContext";
import ScreenCard from "../components/ScreenCard";

export default function ConnectDevice() {
  const { t } = useI18n();
  const [copied, setCopied] = useState(false);
  const url = window.location.origin;
  const isLocal = /localhost|127\.0\.0\.1/.test(url);

  async function copy() {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // sin portapapeles: el usuario puede copiar a mano
    }
  }

  return (
    <ScreenCard>
      <div>
        <h1>{t("connect.title")}</h1>
        <p style={{ margin: "4px 0 0", color: "#0a5a53", fontWeight: 600, fontSize: 14 }}>
          {t("connect.subtitle")}
        </p>
      </div>

      <div style={{ background: "#fff", borderRadius: 20, padding: 18, display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
        <QRCodeSVG value={url} size={188} bgColor="#ffffff" fgColor="#08433e" />
        <code style={{ fontWeight: 800, color: "var(--teal-dark)", wordBreak: "break-all", textAlign: "center" }}>
          {url}
        </code>
        <button onClick={() => void copy()} style={{ width: "100%" }}>
          {copied ? t("connect.copied") : t("connect.copy")}
        </button>
      </div>

      {isLocal && (
        <p role="alert" style={{ background: "rgba(255,255,255,.6)", borderRadius: 12, padding: 12, color: "#0a5a53", fontSize: 13, margin: 0 }}>
          ⚠️ {t("connect.localhostWarn")}
        </p>
      )}

      <Link to="/familia/explorar" style={{ textAlign: "center", marginTop: 4 }}>
        ←
      </Link>
    </ScreenCard>
  );
}
```

## Step 4: `frontend/src/App.tsx`
Importa `import ConnectDevice from "./screens/ConnectDevice";` y, junto a las rutas `/familia/*` dentro de `<ProtectedRoute />`, añade:
```tsx
        <Route path="/familia/conectar" element={<ConnectDevice />} />
```

## Step 5: `frontend/src/screens/WhoExplores.tsx`
Junto a los otros enlaces del pie (Configurar IA / Revisar cuentos), añade:
```tsx
      <Link to="/familia/conectar" style={{ textAlign: "center", marginTop: 4 }}>
        {t("connect.link")}
      </Link>
```

## Step 6: Test `frontend/src/screens/ConnectDevice.test.tsx`
```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { expect, test } from "vitest";
import { I18nProvider } from "../i18n/I18nContext";
import ConnectDevice from "./ConnectDevice";

test("shows the app URL and a QR code", () => {
  render(
    <I18nProvider initialLang="es">
      <MemoryRouter>
        <ConnectDevice />
      </MemoryRouter>
    </I18nProvider>,
  );
  // En jsdom, window.location.origin suele ser http://localhost:3000
  expect(screen.getByText(/conectar otro dispositivo/i)).toBeInTheDocument();
  expect(screen.getByText(new RegExp(window.location.origin.replace(/[.]/g, "\\."), "i"))).toBeInTheDocument();
  expect(document.querySelector("svg")).not.toBeNull(); // el QR es un <svg>
});
```

## Step 7: Verificación
- `npm test` → todo PASS.
- `npm run lint` → limpio.

## Step 8: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): in-app 'connect device' screen with URL + QR"
```
