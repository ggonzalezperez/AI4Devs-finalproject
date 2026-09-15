# Task: Cableado del avatar del niño (frontend + /me/profile)

Frontend `frontend/` + un retoque backend. Rama `feature-avatares`. SIN push (lo hace el controlador).
Ya existe el set diseñado en `frontend/src/components/avatars.tsx` con: `Avatar` (componente), `AVATAR_IDS`, `DEFAULT_AVATAR`, `avatarLabel`, `isAvatarId`, tipo `AvatarId`. NO lo modifiques; úsalo.
A1 ya añadió el campo `avatar` al backend (Child + ChildCreate + ChildRead).

Objetivo: el niño elige un avatar al darse de alta y se ve en la tripulación, en la pantalla de acceso (PIN) y en la cabecera del niño. Sustituye los emojis de `lib/avatar.ts`.

**Files:**
- Modify: `frontend/src/api/children.ts` (tipo + createChild con avatar)
- Modify: `frontend/src/screens/AddExplorer.tsx` (selector de avatar)
- Modify: `frontend/src/screens/WhoExplores.tsx` (mostrar avatar + pasar en navegación)
- Modify: `frontend/src/screens/ChildAccess.tsx` (mostrar avatar elegido)
- Modify: `frontend/src/api/nucleo.ts` (ChildProfile + avatar)
- Modify: `frontend/src/components/ChildHeader.tsx` (mostrar avatar)
- Modify (backend): `backend/app/schemas/knowledge.py` (ChildProfile.avatar) y `backend/app/routers/me.py` (devolver avatar)
- Delete: `frontend/src/lib/avatar.ts` (ya no se usa)
- Modify i18n: `frontend/src/i18n/translations.ts` (`addExplorer.avatar`)
- Tests: actualizar los que mockean hijos/perfil + añadir casos

## Step 1: `frontend/src/api/children.ts`
```ts
export type Child = { id: number; name: string; birthdate: string; age: number; avatar: string };

export function createChild(name: string, birthdate: string, pin: string, avatar: string) {
  return apiFetch<Child>("/children", {
    method: "POST",
    auth: true,
    body: { name, birthdate, pin, avatar },
  });
}
```
(El resto del archivo igual: mantén `listChildren` y `childLogin`.)

## Step 2: i18n — `frontend/src/i18n/translations.ts`
es (junto a otras `addExplorer.*`): `"addExplorer.avatar": "Elige un avatar",`
en: `"addExplorer.avatar": "Choose an avatar",`

## Step 3: `frontend/src/screens/AddExplorer.tsx`
- Importa: `import { Avatar, AVATAR_IDS, DEFAULT_AVATAR, avatarLabel, type AvatarId } from "../components/avatars";`
- Añade estado: `const [avatar, setAvatar] = useState<AvatarId>(DEFAULT_AVATAR);`
- En la llamada de creación: `await createChild(name, birthdate, pin, avatar);`
- En el formulario, **después del badge de edad (`age !== null && ...`) y antes del label del PIN**, añade el selector:
```tsx
        <div>
          <span style={{ display: "block", fontSize: 13, fontWeight: 800, letterSpacing: "0.02em", color: "var(--teal-dark)", marginBottom: 6 }}>
            {t("addExplorer.avatar")}
          </span>
          <div role="radiogroup" aria-label={t("addExplorer.avatar")} style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 }}>
            {AVATAR_IDS.map((id) => (
              <button
                type="button"
                key={id}
                role="radio"
                aria-checked={avatar === id}
                aria-label={avatarLabel(id)}
                onClick={() => setAvatar(id)}
                style={{
                  padding: 3,
                  minHeight: 0,
                  borderRadius: 14,
                  background: avatar === id ? "rgba(255,122,89,.16)" : "transparent",
                  outline: avatar === id ? "2px solid var(--coral)" : "2px solid transparent",
                  boxShadow: "none",
                }}
              >
                <Avatar id={id} size={44} />
              </button>
            ))}
          </div>
        </div>
```
(Las `style` inline anulan la regla `.screen-card button:not(.btn-primary)`.)

## Step 4: `frontend/src/screens/WhoExplores.tsx`
- Quita `import { avatarFor } from "../lib/avatar";`. Añade `import { Avatar } from "../components/avatars";`
- Sustituye `<span style={{ fontSize: 30 }}>{avatarFor(c.id)}</span>` por:
```tsx
            <Avatar id={c.avatar} size={46} />
```
- Al navegar al acceso del niño, pasa también el avatar:
```tsx
            onClick={() => navigate(`/explorar/${c.id}`, { state: { name: c.name, avatar: c.avatar } })}
```

## Step 5: `frontend/src/screens/ChildAccess.tsx`
- Quita `import { avatarFor } from "../lib/avatar";`. Añade `import { Avatar } from "../components/avatars";` y amplía la import de react-router-dom para incluir `useLocation`.
- Lee el avatar del state de navegación:
```tsx
  const location = useLocation();
  const avatar = (location.state as { avatar?: string } | null)?.avatar;
```
- Sustituye `<div style={{ fontSize: 52 }}>{avatarFor(Number(childId))}</div>` por:
```tsx
        <div style={{ display: "flex", justifyContent: "center" }}>
          <Avatar id={avatar} size={72} />
        </div>
```

## Step 6: Backend `/me/profile` — devolver avatar
- `backend/app/schemas/knowledge.py`: en `ChildProfile` añade `avatar: str`.
- `backend/app/routers/me.py`: en `my_profile`, return:
```python
    return ChildProfile(name=child.name, age=child.age, islands=len(nodes), avatar=child.avatar)
```

## Step 7: `frontend/src/api/nucleo.ts`
```ts
export type ChildProfile = { name: string; age: number; islands: number; avatar: string };
```

## Step 8: `frontend/src/components/ChildHeader.tsx`
- Importa `import { Avatar } from "./avatars";`
- Sustituye el bloque `{p?.name && (...)}` por:
```tsx
      {p?.name && (
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Avatar id={p.avatar} size={30} />
          <div style={{ fontFamily: "var(--font-head)", fontWeight: 600, color: "var(--teal-dark)" }}>
            {t("child.hi")} {p.name}
          </div>
        </div>
      )}
```

## Step 9: Borra `frontend/src/lib/avatar.ts`
Tras quitar sus imports (pasos 4 y 5), elimina el archivo. Verifica: `grep -rn "lib/avatar" frontend/src` → vacío.

## Step 10: Tests
Actualiza los mocks que devuelven hijos/perfil para incluir `avatar` y arregla lo que rompa al quitar `avatarFor`:
- `frontend/src/screens/WhoExplores.test.tsx`: añade `avatar: "fox"` a cada hijo del mock; añade `expect(screen.getByLabelText("Zorro")).toBeInTheDocument();`.
- `frontend/src/components/ChildHeader.test.tsx`: añade `avatar: "cat"` al JSON de `/me/profile`.
- `frontend/src/screens/ChildAccess.test.tsx`: que siga verde (Avatar cae a `DEFAULT_AVATAR` si no hay state).
- `frontend/src/screens/AddExplorer.test.tsx`: añade test — `await userEvent.click(screen.getByRole("radio", { name: "Cohete" }))`, completa el formulario válido y al enviar el body del POST a `/children` incluye `avatar: "rocket"`. Reutiliza el patrón de mock de fetch existente; inspecciona el body con `JSON.parse((fetch as any).mock.calls...[1].body)` según cómo lo hagan ya los otros tests.
- Backend `backend/tests/test_me_profile.py`: añade `assert body["avatar"] == "fox"`.

## Step 11: Verificación
- Frontend: `npm test` (verde) y `npm run lint` (limpio).
- Backend: `./.venv/Scripts/python.exe -m pytest -q` (verde).

## Step 12: Commit (local, SIN push)
```bash
git add frontend/ backend/
git commit -m "feat(frontend): designed child avatars (picker + crew + access + header)"
```
