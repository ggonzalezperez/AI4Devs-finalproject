# Task UX5: Info/ayuda en onboarding (sencillo, intuitivo, con información)

Frontend `frontend/`. Rama `feature-ux-improvements`. SIN push.

**Files:**
- Modify: `frontend/src/screens/WhoExplores.tsx` (aviso de modo demo + configurar IA)
- Modify: `frontend/src/screens/AddExplorer.tsx` (pista del PIN)
- Modify: `frontend/src/i18n/translations.ts` (claves nuevas)

## Step 1: Claves i18n (es y en)
es:
```
    "who.demoHint": "💡 Por defecto funciona en modo demo. Configura la IA para lecciones reales.",
    "addExplorer.pinHint": "Tu hijo usará este PIN para entrar en su espacio.",
```
en:
```
    "who.demoHint": "💡 It runs in demo mode by default. Set up AI for real lessons.",
    "addExplorer.pinHint": "Your child will use this PIN to enter their space.",
```

## Step 2: `frontend/src/screens/WhoExplores.tsx`
Lee el archivo. Justo **encima** del enlace `<Link to="/familia/ia">` (el de "⚙️ Configurar IA"), añade un aviso pequeño:
```tsx
      <p style={{ fontSize: 12, color: "#0a5a53", textAlign: "center", margin: "8px 0 0" }}>
        {t("who.demoHint")}
      </p>
```
(usa el `t` ya disponible en el componente.)

## Step 3: `frontend/src/screens/AddExplorer.tsx`
Lee el archivo. Dentro del bloque del campo PIN (`{t("field.pin")}` ... input), añade **debajo del input del PIN** (no del de repetir) una pista:
```tsx
          <small style={{ color: "#0a5a53", fontWeight: 600 }}>{t("addExplorer.pinHint")}</small>
```
(colócala dentro del `<label>` del PIN, tras el `<input>`, o como hermano inmediato — lo que no rompa el test; el test de AddExplorer usa `getByLabelText(/Clave de 4 dígitos/i)` y `getByLabelText("Repite la clave")`, así que NO metas texto en bloque dentro de esos `<label>` que altere su nombre accesible; si dudas, ponla como `<small>` hermano del `<label>` del PIN).

## Step 4: Tests + suite + lint
`npm test` → todo PASS. `npm run lint` → limpio. (Si algún `getByLabelText` se rompe por meter el `<small>` dentro del label, muévelo fuera del label.)

## Step 5: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): onboarding hints (demo mode + PIN explanation)"
```
