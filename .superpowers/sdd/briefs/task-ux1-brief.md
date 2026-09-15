# Task UX1: Mejorar UI/UX del panel de IA (sencillo, intuitivo, con información)

Frontend `frontend/`. Rama `feature-ux-improvements`. SIN push.
Objetivo: que una familia entienda de un vistazo los 3 niveles y configure sin dudas. Más claridad e info, sin romper tests.

**Files:**
- Modify: `frontend/src/screens/AIConfigPanel.tsx`
- Modify: `frontend/src/i18n/translations.ts` (claves nuevas `aiPanel.*`)
- (El test `AIConfigPanel.test.tsx` debe seguir pasando; ajústalo solo si cambian etiquetas usadas por el test — mantiene: selecciona "Proveedor", escribe en "Clave API", pulsa "Guardar". NO cambies esas etiquetas.)

## Step 1: Añadir claves i18n (es y en, dentro de los objetos existentes)
es:
```
    "aiPanel.intro": "Elige cómo se crean las lecciones de tus hijos:",
    "aiPanel.tierFree": "🟢 Gratis: modelo local (Ollama) o demo. Sin coste.",
    "aiPanel.tierByok": "🔑 Tu clave: usa tu cuenta de Claude/OpenAI/… Pagas a tu proveedor.",
    "aiPanel.tierManaged": "💼 Comercial: nos encargamos nosotros (próximamente).",
    "aiPanel.keyNote": "🔒 Tu clave se guarda cifrada y nunca se muestra.",
    "aiPanel.useThis": "Usar este modelo",
    "aiPanel.localHelp": "Necesitas Ollama corriendo y el modelo descargado.",
    "aiPanel.byokHelp": "Pega tu clave API; se guarda cifrada.",
    "aiPanel.freeHelp": "Modo demo: lecciones de ejemplo, sin IA real.",
```
en:
```
    "aiPanel.intro": "Choose how your kids' lessons are created:",
    "aiPanel.tierFree": "🟢 Free: local model (Ollama) or demo. No cost.",
    "aiPanel.tierByok": "🔑 Your key: use your Claude/OpenAI/… account. You pay your provider.",
    "aiPanel.tierManaged": "💼 Commercial: we handle it (coming soon).",
    "aiPanel.keyNote": "🔒 Your key is stored encrypted and never shown.",
    "aiPanel.useThis": "Use this model",
    "aiPanel.localHelp": "You need Ollama running and the model pulled.",
    "aiPanel.byokHelp": "Paste your API key; it is stored encrypted.",
    "aiPanel.freeHelp": "Demo mode: example lessons, no real AI.",
```

## Step 2: Mejorar `frontend/src/screens/AIConfigPanel.tsx`
Aplica estas mejoras manteniendo la lógica existente (estado, save, recommend):
1. **Bajo el subtítulo**, añade una tarjeta de info con los 3 niveles:
```tsx
      <div style={{ background: "rgba(255,255,255,.6)", borderRadius: 14, padding: "12px 14px", fontSize: 13, color: "#0a5a53", lineHeight: 1.5 }}>
        <div style={{ fontWeight: 700, marginBottom: 4 }}>{t("aiPanel.intro")}</div>
        <div>{t("aiPanel.tierFree")}</div>
        <div>{t("aiPanel.tierByok")}</div>
        <div>{t("aiPanel.tierManaged")}</div>
      </div>
```
2. **Bajo el selector de proveedor**, una línea de ayuda según el proveedor elegido:
```tsx
        <p style={{ margin: "2px 0 0", fontSize: 12, color: "#0a5a53" }}>
          {provider === "ollama" ? t("aiPanel.localHelp") : current?.needs_key ? t("aiPanel.byokHelp") : t("aiPanel.freeHelp")}
        </p>
```
(colócala dentro del bloque del `<label>` de proveedor o justo después del select.)
3. **Junto al campo de clave**, añade la nota de cifrado:
```tsx
            <small style={{ color: "#0a5a53" }}>{t("aiPanel.keyNote")}</small>
```
4. **En el recomendador**, cuando hay `rec`, añade un botón "Usar este modelo" que aplica el modelo local recomendado:
```tsx
            <button
              onClick={() => {
                setProvider("ollama");
                setModel(rec.recommended);
              }}
              style={{ marginTop: 6, padding: "8px 12px" }}
            >
              {t("aiPanel.useThis")}
            </button>
```
Mantén el texto `rec.note` y `rec.recommended` ya existentes.

## Step 3: Tests + suite + lint
`npm test src/screens/AIConfigPanel.test.tsx` → PASS. Luego `npm test` y `npm run lint` → todo verde. (Si algún test global se rompe por las claves i18n, arréglalo mínimamente.)

## Step 4: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): clearer AI settings panel (tier info, help text, key note, use-recommended)"
```
