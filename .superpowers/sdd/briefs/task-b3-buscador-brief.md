# Task B3: Buscador del archipiélago

Frontend `frontend/`. Rama `feature-lecciones-ricas`. SIN push.
En "Mis islas" (`MyKnowledge.tsx`), añade un **buscador** para reencontrar islas ya usadas: filtra por concepto/materia mientras se escribe (sin acentos ni mayúsculas). Solo frontend (las islas ya se cargan con `getKnowledge`).

**Files:**
- Modify: `frontend/src/screens/MyKnowledge.tsx`
- Modify: `frontend/src/i18n/translations.ts` (`islands.search`, `islands.noMatch`)
- Modify test: `frontend/src/screens/MyKnowledge.test.tsx`

## Step 1: i18n
es:
```
    "islands.search": "Buscar una isla…",
    "islands.noMatch": "No encuentro esa isla. Prueba otra palabra.",
```
en:
```
    "islands.search": "Search an island…",
    "islands.noMatch": "No island found. Try another word.",
```

## Step 2: `frontend/src/screens/MyKnowledge.tsx`
Lee el archivo actual (ya tiene la cabecera, la pista `islands.tapHint`, y el `nodes.map` con islas enlazadas a su conversación por `root_lesson_id`). Añade:
- Un estado de búsqueda: `const [query, setQuery] = useState("");`
- Un helper de normalización (sin acentos, minúsculas):
```tsx
  const norm = (s: string) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  const filtered = query.trim()
    ? nodes.filter((n) => norm(n.concept).includes(norm(query)) || norm(n.subject).includes(norm(query)))
    : nodes;
```
- Un input de búsqueda **encima de la rejilla de islas**, visible solo cuando hay islas:
```tsx
      {loaded && nodes.length > 0 && (
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t("islands.search")}
          aria-label={t("islands.search")}
        />
      )}
```
- Cambia el `nodes.map(...)` por `filtered.map(...)` (mantén EXACTAMENTE la estructura actual de cada isla, incluido el enlace por `root_lesson_id`).
- Añade un mensaje cuando hay islas pero el filtro no devuelve nada:
```tsx
      {loaded && nodes.length > 0 && filtered.length === 0 && (
        <p style={{ color: "#0a5a53" }}>{t("islands.noMatch")}</p>
      )}
```
(Mantén el mensaje `islands.empty` existente para cuando NO hay ninguna isla.)

## Step 3: Test `frontend/src/screens/MyKnowledge.test.tsx`
Mantén el test existente verde. Añade uno que, con varias islas mockeadas, al escribir en el buscador filtra:
```tsx
import { fireEvent } from "@testing-library/react";
// ... render con nodes: [{concept:"flotabilidad",...}, {concept:"volcanes",...}] (incluye root_lesson_id en cada uno)
// tras render:
const search = await screen.findByLabelText(/buscar una isla/i);
fireEvent.change(search, { target: { value: "volca" } });
expect(screen.getByText("volcanes")).toBeInTheDocument();
expect(screen.queryByText("flotabilidad")).not.toBeInTheDocument();
```
(Ajusta los conceptos/campos al shape real de `KnowledgeNode`, incluyendo `root_lesson_id`.)

## Step 4: Verificación
- `npm test` → todo PASS.
- `npm run lint` → limpio.

## Step 5: Commit (local, SIN push)
```bash
git add frontend/
git commit -m "feat(frontend): archipelago search to find islands already explored"
```
