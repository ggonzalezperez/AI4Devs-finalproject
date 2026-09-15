# Task B2c: Abrir la conversación al pinchar una isla

Backend `backend/` (venv `./.venv/Scripts/python.exe`) + Frontend `frontend/`. Rama `feature-lecciones-ricas`. SIN push. TDD, migración NO destructiva.
Cierra el bucle: cada **isla** (KnowledgeNode) recuerda la **conversación raíz** que la creó; al pincharla en el archipiélago se abre ese chat (`/jugar/leccion/{root}`), que ya recupera el hilo y permite seguir preguntando.

Decisión: añadir `root_lesson_id` a `knowledge_nodes`, fijado cuando se crea la isla (en `ensure_node`, llamado al generar cada turno). Para la lección raíz el root es su propio id; para un turno hijo es `root_id`.

**Files:**
- Modify: `backend/app/models/knowledge.py` (columna `root_lesson_id`)
- Modify: `backend/app/repositories/knowledge.py` (`ensure_node` acepta y fija `root_lesson_id`)
- Modify: `backend/app/services/lesson_service.py` (pasar el root al asegurar la isla)
- Modify: `backend/app/schemas/knowledge.py` (`KnowledgeNodeRead.root_lesson_id`)
- Migración Alembic (add_column, no destructiva)
- Modify: `frontend/src/api/nucleo.ts` (tipo KnowledgeNode + root_lesson_id)
- Modify: `frontend/src/screens/MyKnowledge.tsx` (isla enlaza a su conversación)
- Modify: `frontend/src/i18n/translations.ts` (`islands.tapHint`)
- Tests (backend + frontend)

## Step 1: `backend/app/models/knowledge.py`
Añade (Integer ya importado):
```python
    root_lesson_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

## Step 2: `backend/app/repositories/knowledge.py`
Cambia `ensure_node` para aceptar y fijar el root al crear (NO lo cambies si ya existe):
```python
def ensure_node(
    db: Session, child_id: int, concept: str, subject: str, root_lesson_id: int | None = None
) -> KnowledgeNode:
    existing = db.execute(
        select(KnowledgeNode).where(
            KnowledgeNode.child_id == child_id, KnowledgeNode.concept == concept
        )
    ).scalar_one_or_none()
    if existing:
        return existing
    node = KnowledgeNode(
        child_id=child_id, concept=concept, subject=subject, root_lesson_id=root_lesson_id
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node
```
(`upsert_node` se queda igual.)

## Step 3: `backend/app/services/lesson_service.py`
En las DOS llamadas a `ensure_node` (en `create_lesson` y en `continue_conversation`), pasa el id de la conversación raíz:
- En `create_lesson` (la lección recién creada puede ser raíz → su root es ella misma):
```python
    knowledge_repo.ensure_node(
        db, child.id, lesson.concept, lesson.subject, root_lesson_id=lesson.root_id or lesson.id
    )
```
- En `continue_conversation` (ya tienes `root_id` calculado; el turno hijo comparte ese root):
```python
    knowledge_repo.ensure_node(
        db, child.id, lesson.concept, lesson.subject, root_lesson_id=lesson.root_id or lesson.id
    )
```
(En ambos casos `lesson.root_id or lesson.id` da el id de la raíz del hilo.)

## Step 4: `backend/app/schemas/knowledge.py`
En `KnowledgeNodeRead` añade:
```python
    root_lesson_id: int | None = None
```

## Step 5: Migración
- `./.venv/Scripts/alembic.exe revision --autogenerate -m "knowledge node root_lesson_id"`
- Verifica que SOLO añade `op.add_column('knowledge_nodes', sa.Column('root_lesson_id', sa.Integer(), nullable=True))` (+ downgrade). Si hay drops/alters sobre otras tablas, DETENTE y reporta DONE_WITH_CONCERNS sin aplicar.
- Aplica: `./.venv/Scripts/alembic.exe upgrade head`.

## Step 6: Backend test
Reutiliza el patrón de token de niño. Verifica:
- Tras crear una lección raíz, `GET /me/knowledge` devuelve un nodo cuyo `root_lesson_id` == id de esa lección.
- Tras `POST /lessons/{root}/ask` con una pregunta de OTRO concepto, la isla nueva tiene `root_lesson_id` == id de la raíz (no del turno hijo).
- Mantén verdes los tests existentes. `./.venv/Scripts/python.exe -m pytest -q` → todo PASS.

## Step 7: `frontend/src/api/nucleo.ts`
En el tipo `KnowledgeNode`, añade el campo:
```ts
  root_lesson_id: number | null;
```

## Step 8: i18n — `frontend/src/i18n/translations.ts`
es: `"islands.tapHint": "Toca una isla para seguir descubriendo 💬",`
en: `"islands.tapHint": "Tap an island to keep exploring 💬",`

## Step 9: `frontend/src/screens/MyKnowledge.tsx`
- Importa `Link` (ya importa de react-router-dom; añade `Link` si falta — ya lo usa para "Descubrir más").
- Bajo el `<h1>{t("islands.title")}</h1>`, añade una pista cuando hay islas:
```tsx
      {loaded && nodes.length > 0 && (
        <p style={{ margin: 0, color: "#0a5a53", fontWeight: 600, fontSize: 13 }}>{t("islands.tapHint")}</p>
      )}
```
- Sustituye el `nodes.map(...)` para que cada isla con `root_lesson_id` sea un enlace a su conversación:
```tsx
        {nodes.map((n) => {
          const card = (
            <div style={{ background: "#fff", borderRadius: 16, padding: "12px 14px", minWidth: 120 }}>
              <div style={{ fontSize: 26 }}>🏝️</div>
              <strong style={{ color: "var(--teal-dark)" }}>{n.concept}</strong>
              <div style={{ fontSize: 12, color: "#0a5a53" }}>
                {n.subject} · ⭐ {n.mastery}
              </div>
            </div>
          );
          return n.root_lesson_id ? (
            <Link key={n.id} to={`/jugar/leccion/${n.root_lesson_id}`} style={{ textDecoration: "none" }}>
              {card}
            </Link>
          ) : (
            <div key={n.id}>{card}</div>
          );
        })}
```

## Step 10: Frontend test — `frontend/src/screens/MyKnowledge.test.tsx`
Añade `root_lesson_id` al nodo mockeado (p. ej. `root_lesson_id: 9`) y comprueba que la isla es un enlace a la conversación:
```tsx
const link = await screen.findByRole("link", { name: /flotabilidad/i });
expect(link).toHaveAttribute("href", "/jugar/leccion/9");
```
(Si el mock actual no tiene `root_lesson_id`, añádelo; mantén verde lo demás. Si el test usa otro concepto, ajusta el nombre.)

## Step 11: Verificación
- Backend: `./.venv/Scripts/python.exe -m pytest -q` (verde).
- Frontend: `npm test` (verde) + `npm run lint` (limpio).

## Step 12: Commit (local, SIN push)
```bash
git add backend/ frontend/
git commit -m "feat: open an island's saved conversation from the archipelago"
```
