# Task IMG-2b: Imágenes — panel de config + render en el chat (frontend)

Frontend `frontend/`. Rama `feature-imagenes`. SIN push.
Añade al panel de IA una sección "Imágenes en las lecciones" (proveedor + modelo + URL local + clave + activar) y muestra la imagen generada en cada turno del chat. IMG-1/2a (backend) ya exponen los campos `image_*` en `/family/ai-config` y `image_url` en la lección.

**Files:**
- Modify: `frontend/src/api/client.ts` (helper `assetUrl`)
- Modify: `frontend/src/api/aiConfig.ts` (tipos con campos de imagen)
- Modify: `frontend/src/screens/AIConfigPanel.tsx` (sección de imagen)
- Modify: `frontend/src/api/nucleo.ts` (`Lesson.image_url`)
- Modify: `frontend/src/screens/LessonScreen.tsx` (render `<img>` en el turno)
- Modify: `frontend/src/i18n/translations.ts` (claves `aiPanel.img*`)
- Modify tests: `frontend/src/screens/AIConfigPanel.test.tsx` (mock con `image_providers`)

## Step 1: `frontend/src/api/client.ts`
Añade (BASE_URL ya existe en el módulo):
```ts
export function assetUrl(path: string): string {
  return `${BASE_URL}${path}`;
}
```

## Step 2: `frontend/src/api/aiConfig.ts`
- En `AIConfig` añade:
```ts
  image_provider: string;
  image_model: string | null;
  image_base_url: string | null;
  image_enabled: boolean;
  has_image_api_key: boolean;
```
- En `Catalog` añade: `image_providers: Provider[];`
- En `AIConfigUpdate` añade:
```ts
  image_provider?: string;
  image_model?: string | null;
  image_base_url?: string | null;
  image_api_key?: string | null;
  image_enabled?: boolean;
```

## Step 3: i18n — `frontend/src/i18n/translations.ts`
es:
```
    "aiPanel.imgTitle": "🖼️ Imágenes en las lecciones",
    "aiPanel.imgHelp": "Si activas un modelo de imagen, cada lección incluirá una ilustración acorde a la edad. Gratis con HuggingFace (token) o local con SDXL; OpenAI/Gemini de pago.",
    "aiPanel.imgEnable": "Activar imágenes",
```
en:
```
    "aiPanel.imgTitle": "🖼️ Images in lessons",
    "aiPanel.imgHelp": "If you enable an image model, each lesson includes an age-appropriate illustration. Free with HuggingFace (token) or local with SDXL; OpenAI/Gemini are paid.",
    "aiPanel.imgEnable": "Enable images",
```

## Step 4: `frontend/src/screens/AIConfigPanel.tsx`
- Añade estado (junto a los existentes):
```tsx
  const [imageProvider, setImageProvider] = useState("none");
  const [imageModel, setImageModel] = useState("");
  const [imageBaseUrl, setImageBaseUrl] = useState("");
  const [imageApiKey, setImageApiKey] = useState("");
  const [imageEnabled, setImageEnabled] = useState(false);
  const [hasImageKey, setHasImageKey] = useState(false);
```
- En el `useEffect`, dentro del `.then((c: AIConfig) => {...})`, añade:
```tsx
        setImageProvider(c.image_provider);
        setImageModel(c.image_model ?? "");
        setImageBaseUrl(c.image_base_url ?? "");
        setImageEnabled(c.image_enabled);
        setHasImageKey(c.has_image_api_key);
```
- Tras `const modelOptions = ...`, añade los derivados de imagen:
```tsx
  const imageProviders = catalog.image_providers ?? [];
  const currentImg = imageProviders.find((p) => p.id === imageProvider);
  const imgModelOptions = currentImg?.models ?? [];
```
- En `save()`, amplía el payload de `putAIConfig` con los campos de imagen:
```tsx
        image_provider: imageProvider,
        image_model: imageModel || null,
        image_base_url: currentImg?.needs_base_url ? imageBaseUrl || null : null,
        image_api_key: imageApiKey ? imageApiKey : undefined,
        image_enabled: imageEnabled,
```
y tras `setHasKey(cfg.has_api_key);` añade `setHasImageKey(cfg.has_image_api_key); setImageApiKey("");`
- Añade el BLOQUE DE UI de imagen **justo después** del `</div>` que cierra el bloque de config de texto (el que contiene el botón Guardar) y **antes** del bloque de hardware:
```tsx
      <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 12, background: "#fff", borderRadius: 16, padding: 16 }}>
        <strong>{t("aiPanel.imgTitle")}</strong>
        <small style={{ color: "#0a5a53" }}>{t("aiPanel.imgHelp")}</small>
        <label style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
          <input type="checkbox" checked={imageEnabled} onChange={(e) => setImageEnabled(e.target.checked)} />
          {t("aiPanel.imgEnable")}
        </label>
        <label>
          {t("aiPanel.provider")}
          <select value={imageProvider} onChange={(e) => { setImageProvider(e.target.value); setImageModel(""); }}>
            {imageProviders.map((p) => (
              <option key={p.id} value={p.id} disabled={!p.enabled}>
                {p.label}{p.enabled ? "" : ` — ${t("aiPanel.soon")}`}
              </option>
            ))}
          </select>
        </label>
        {imgModelOptions.length > 0 && (
          <label>
            {t("aiPanel.model")}
            <select value={imageModel} onChange={(e) => setImageModel(e.target.value)}>
              <option value="">—</option>
              {imgModelOptions.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </label>
        )}
        {currentImg?.needs_base_url && (
          <label>
            {t("aiPanel.baseUrl")}
            <input value={imageBaseUrl} onChange={(e) => setImageBaseUrl(e.target.value)} placeholder="http://localhost:7860" />
          </label>
        )}
        {currentImg?.needs_key && (
          <>
            <label>
              {t("aiPanel.apiKey")}
              <input
                type="password"
                value={imageApiKey}
                onChange={(e) => setImageApiKey(e.target.value)}
                placeholder={hasImageKey ? t("aiPanel.apiKeySaved") : "hf_... / sk-..."}
              />
            </label>
            <small style={{ color: "#0a5a53" }}>{t("aiPanel.keyNote")}</small>
          </>
        )}
      </div>
```
(El botón "Guardar" del bloque de texto guarda TODO, incluido lo de imagen, porque `save()` ya envía los campos de imagen.)

## Step 5: `frontend/src/api/nucleo.ts`
En el tipo `Lesson` añade: `image_url: string | null;`

## Step 6: `frontend/src/screens/LessonScreen.tsx`
- Importa `assetUrl`: cambia el import de `../api/client` para incluirlo, o añade `import { assetUrl } from "../api/client";`
- Dentro de `ChatTurn`, en la burbuja de Chispa, **justo después del `<div>` del título** (`{turn.title}`) y antes del cuerpo, añade la imagen si existe:
```tsx
        {turn.image_url && (
          <img
            src={assetUrl(turn.image_url)}
            alt={turn.title}
            style={{ width: "100%", borderRadius: 12, margin: "8px 0" }}
          />
        )}
```

## Step 7: Tests
- `frontend/src/screens/AIConfigPanel.test.tsx`: el mock del catálogo (`/family/ai-config/catalog`) debe incluir ahora `image_providers` (p. ej. `[{id:"none",label:"Sin imágenes",tier:"free",needs_key:false,needs_base_url:false,enabled:true,models:[]},{id:"huggingface",label:"HuggingFace",tier:"free",needs_key:true,needs_base_url:false,enabled:true,models:["black-forest-labs/FLUX.1-schnell"]}]`), y el mock de `/family/ai-config` debe incluir los campos `image_provider:"none"`, `image_model:null`, `image_base_url:null`, `image_enabled:false`, `has_image_api_key:false`. Añade una aserción de que la sección se ve: `expect(await screen.findByText(/Imágenes en las lecciones/i)).toBeInTheDocument();`. Mantén verdes las aserciones existentes.
- Si algún test de LessonScreen mockea turnos, añade `image_url: null` al turno para que TypeScript compile (Avatar/render no se afecta).

## Step 8: Verificación
- `npm test` → todo PASS.
- `npm run lint` → limpio.

## Step 9: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): image config panel section + lesson image render"
```
