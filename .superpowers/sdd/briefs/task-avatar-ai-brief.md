# Task Avatar-IA: Generar avatar del niño con IA (reusa la costura de imagen)

Backend `backend/` (venv `./.venv/Scripts/python.exe`) + Frontend `frontend/`. Rama `feature-fasec-extra`. SIN push. TDD, migración NO destructiva.
Además del set curado de avatares SVG, la familia puede **generar un avatar con IA** describiéndolo. Reusa `build_image_generator` (IMG-1). Si la generación de imágenes NO está activada → error claro pidiendo activarla en el panel. El avatar generado (imagen) tiene prioridad sobre el SVG curado al mostrarse.

**Files backend:**
- Modify: `app/models/child.py` (`avatar_image_url`)
- Modify: `app/schemas/child.py` (`ChildRead.avatar_image_url`; nuevo `AvatarGenerate`)
- Modify: `app/schemas/knowledge.py` (`ChildProfile.avatar_image_url`)
- Modify: `app/routers/me.py` (devolver avatar_image_url en /me/profile)
- Modify: `app/services/image_generator.py` (`build_avatar_prompt`)
- Modify: `app/routers/children.py` (endpoint generar avatar)
- Migración Alembic (add_column, no destructiva)
**Files frontend:**
- Modify: `frontend/src/api/children.ts` (Child + generateChildAvatar)
- Modify: `frontend/src/api/nucleo.ts` (ChildProfile + avatar_image_url)
- Modify: `frontend/src/components/avatars.tsx` (Avatar acepta `imageUrl`)
- Modify: `frontend/src/screens/WhoExplores.tsx` (pasar imageUrl + enlace a generar)
- Modify: `frontend/src/components/ChildHeader.tsx` (pasar imageUrl)
- Create: `frontend/src/screens/ChildAvatar.tsx` + ruta en `App.tsx`
- Modify: `frontend/src/i18n/translations.ts`
- Tests (backend + frontend)

## BACKEND

### Step 1: `app/models/child.py`
Añade (String ya importado): `avatar_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)`

### Step 2: `app/schemas/child.py`
- En `ChildRead` añade: `avatar_image_url: str | None = None`
- Añade un schema nuevo:
```python
class AvatarGenerate(BaseModel):
    description: str = Field(min_length=2, max_length=120)
```

### Step 3: `app/schemas/knowledge.py`
En `ChildProfile` añade: `avatar_image_url: str | None = None`

### Step 4: `app/routers/me.py`
En `my_profile`, añade `avatar_image_url=child.avatar_image_url` al construir `ChildProfile(...)`.

### Step 5: `app/services/image_generator.py`
Añade:
```python
def build_avatar_prompt(description: str) -> str:
    return (
        f"Avatar de perfil de {description}. Ilustración infantil colorida y simpática, "
        "primer plano, fondo liso, sin texto. Apto y seguro para niños."
    )
```

### Step 6: `app/routers/children.py` — endpoint
Lee el archivo para reutilizar el patrón de obtención del niño con verificación de familia (el endpoint de login del niño ya valida que el niño pertenece a la familia del usuario; usa el mismo mecanismo: cargar el `Child` y comprobar `child.family_id == user.family_id`, si no → 404).
Importa lo necesario (`get_settings`, `Path`, `ai_config_repo`, `build_image_generator`, `build_avatar_prompt`, `AvatarGenerate`, `ChildRead`) y añade:
```python
@router.post("/{child_id}/avatar/generate", response_model=ChildRead)
def generate_child_avatar(
    child_id: int,
    payload: AvatarGenerate,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> ChildRead:
    child = db.get(Child, child_id)
    if child is None or child.family_id != user.family_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explorador no encontrado")
    cfg = ai_config_repo.get_or_create(db, user.family_id)
    generator = build_image_generator(cfg)
    try:
        img = generator.generate(build_avatar_prompt(payload.description))
    except Exception:
        img = None
    if img is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La generación de imágenes no está activada. Actívala en «Configurar IA».",
        )
    media = Path(get_settings().media_dir) / "avatars"
    media.mkdir(parents=True, exist_ok=True)
    (media / f"{child_id}.png").write_bytes(img.data)
    child.avatar_image_url = f"/media/avatars/{child_id}.png"
    db.commit()
    db.refresh(child)
    return child
```
(Ajusta los imports existentes del router: probablemente ya importa `Child`, `User`, `get_current_family_user`, `get_db`, `status`, `HTTPException`. Añade los que falten.)

### Step 7: Migración
- `./.venv/Scripts/alembic.exe revision --autogenerate -m "child avatar_image_url"`
- Verifica que SOLO añade `op.add_column('children', sa.Column('avatar_image_url', ...))`. Si hay drops/alters sobre otras tablas, DETENTE y reporta DONE_WITH_CONCERNS sin aplicar.
- Aplica: `./.venv/Scripts/alembic.exe upgrade head`.

### Step 8: Backend test
- `build_avatar_prompt("un zorro astronauta")` contiene "zorro astronauta".
- Con imagen desactivada (config por defecto), `POST /children/{id}/avatar/generate` con descripción → **409** (no activada).
- (Opcional) Con un generador inyectado/monkeypatch que devuelve `GeneratedImage(b"PNG")` y `image_enabled`, devuelve 200 y `avatar_image_url` no nulo. Si es complejo de montar, basta el caso 409 + el test del prompt.
- Mantén verdes los tests existentes.

## FRONTEND

### Step 9: `frontend/src/api/children.ts`
- En `Child` añade: `avatar_image_url: string | null;`
- Añade:
```ts
export function generateChildAvatar(childId: number, description: string) {
  return apiFetch<Child>(`/children/${childId}/avatar/generate`, {
    method: "POST",
    auth: true,
    body: { description },
  });
}
```

### Step 10: `frontend/src/api/nucleo.ts`
En `ChildProfile` añade: `avatar_image_url: string | null;`

### Step 11: `frontend/src/components/avatars.tsx`
- Importa `assetUrl`: `import { assetUrl } from "../api/client";`
- En `Avatar`, añade prop opcional `imageUrl?: string | null`. Si viene, renderiza la imagen en vez del SVG:
```tsx
export function Avatar({ id, size = 48, title, imageUrl }: { id?: string | null; size?: number; title?: string; imageUrl?: string | null }) {
  if (imageUrl) {
    return (
      <img
        src={assetUrl(imageUrl)}
        alt={title ?? "avatar"}
        width={size}
        height={size}
        style={{ display: "block", flexShrink: 0, borderRadius: 14, objectFit: "cover" }}
      />
    );
  }
  // ...resto igual (SVG)...
}
```

### Step 12: `frontend/src/screens/WhoExplores.tsx`
- Pasa la imagen al avatar: `<Avatar id={c.avatar} imageUrl={c.avatar_image_url} size={46} />`
- Añade un enlace por niño para generar avatar (junto al nombre o como pequeño botón). Lo más simple: tras el nombre, un `<Link to={`/familia/explorador/${c.id}`} onClick={(e)=>e.stopPropagation()}>✨</Link>` (con `stopPropagation` para no disparar el onClick de la fila que navega al acceso). Colócalo dentro del botón de la fila con cuidado, o añade una fila de acciones. Si complica, añade debajo de la lista un enlace genérico "✨ Personalizar avatares" que lleve a `/familia/explorar` (no ideal) — MEJOR: pon el `<Link>✨</Link>` dentro de la tarjeta del niño, con `stopPropagation`.

### Step 13: `frontend/src/components/ChildHeader.tsx`
Pasa la imagen: `<Avatar id={p.avatar} imageUrl={p.avatar_image_url} size={30} />`

### Step 14: `frontend/src/screens/ChildAvatar.tsx` (nueva) + ruta
```tsx
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { listChildren, generateChildAvatar, type Child } from "../api/children";
import { ApiError } from "../api/client";
import { useI18n } from "../i18n/I18nContext";
import { Avatar } from "../components/avatars";
import Button from "../components/Button";
import ScreenCard from "../components/ScreenCard";

export default function ChildAvatar() {
  const { childId } = useParams();
  const id = Number(childId);
  const { t } = useI18n();
  const [child, setChild] = useState<Child | null>(null);
  const [desc, setDesc] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    listChildren().then((cs) => setChild(cs.find((c) => c.id === id) ?? null)).catch(() => undefined);
  }, [id]);

  async function generate() {
    if (!desc.trim()) return;
    setBusy(true);
    setError("");
    try {
      const updated = await generateChildAvatar(id, desc.trim());
      setChild(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("avatarAI.error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScreenCard>
      <Link to="/familia/explorar">←</Link>
      <h1>{t("avatarAI.title")}</h1>
      <p style={{ color: "#0a5a53", fontWeight: 600, fontSize: 14, margin: 0 }}>{t("avatarAI.subtitle")}</p>
      <div style={{ display: "flex", justifyContent: "center", margin: "8px 0" }}>
        <Avatar id={child?.avatar} imageUrl={child?.avatar_image_url} size={120} />
      </div>
      <input
        value={desc}
        onChange={(e) => setDesc(e.target.value)}
        placeholder={t("avatarAI.placeholder")}
        aria-label={t("avatarAI.placeholder")}
      />
      {error && <p role="alert" style={{ color: "#c0392b", fontWeight: 700, margin: 0 }}>{error}</p>}
      <Button onClick={() => void generate()} disabled={busy}>
        {busy ? t("avatarAI.generating") : t("avatarAI.generate")}
      </Button>
    </ScreenCard>
  );
}
```
En `App.tsx`: importa y añade dentro de `<ProtectedRoute />`:
```tsx
        <Route path="/familia/explorador/:childId" element={<ChildAvatar />} />
```

### Step 15: i18n (es + en)
es:
```
    "avatarAI.title": "✨ Avatar con IA",
    "avatarAI.subtitle": "Describe el avatar y la IA lo dibuja (necesita imágenes activadas en «Configurar IA»).",
    "avatarAI.placeholder": "p. ej. un zorro astronauta",
    "avatarAI.generate": "✨ Generar avatar",
    "avatarAI.generating": "Dibujando…",
    "avatarAI.error": "No se pudo generar el avatar",
```
en:
```
    "avatarAI.title": "✨ AI avatar",
    "avatarAI.subtitle": "Describe the avatar and the AI draws it (needs images enabled in “Set up AI”).",
    "avatarAI.placeholder": "e.g. an astronaut fox",
    "avatarAI.generate": "✨ Generate avatar",
    "avatarAI.generating": "Drawing…",
    "avatarAI.error": "Could not generate the avatar",
```

### Step 16: Tests frontend
- Actualiza los mocks que devuelven hijos/perfil para incluir `avatar_image_url: null` (WhoExplores.test, ChildHeader.test) para que TypeScript compile.
- Añade un test de `ChildAvatar` o de `Avatar` con `imageUrl`: `render(<Avatar imageUrl="/media/avatars/1.png" title="x" />)` → hay un `<img>` cuyo `src` termina en `/media/avatars/1.png`.

## Verificación
- Backend: `./.venv/Scripts/python.exe -m pytest -q` + `./.venv/Scripts/ruff.exe check app tests` → verde/limpio.
- Frontend: `npm test` + `npm run lint` → verde/limpio.

## Commit (local, SIN push)
```bash
git add backend/ frontend/
git commit -m "feat: AI-generated child avatars (reuses image seam, falls back to curated set)"
```
