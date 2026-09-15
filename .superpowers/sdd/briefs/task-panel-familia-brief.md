# Brief — panel-familia: Panel de familia (US5/US6)

> Rama: `entrega_2` · Fecha: 2026-09-14

## Contexto

`RF-PLT-01` (prioridad **Alta**) es el único requisito del MVP sin implementar. La auditoría del
14-09-2026 lo confirmó: [`FamilyLanding.tsx`](../../../frontend/src/screens/FamilyLanding.tsx) es un
redirector de 37 líneas, no un panel.

La familia no tiene hoy **ninguna** forma de ver qué está aprendiendo su hijo. La memoria pedagógica
existe (`knowledge_nodes`), pero es invisible para quien debe acompañar. US5/US6 lo formula como
«padres con control, niño con agencia»: sin esto, solo hay agencia.

**Hallazgo de la auditoría que condiciona el diseño:** la HU (Bloque 5) supone que el panel se
alimenta de los endpoints `/me/*`, pero `/me/*` exige token `child`
([`me.py:21-42`](../../../backend/app/routers/me.py#L21-L42)). Una familia no puede llamarlos, y
darle acceso rompería el JWT tipado, que es garantía de seguridad. **Se corrige la HU, no el diseño
de seguridad:** hacen falta endpoints nuevos con token `family`.

## Alcance

**Entra:**

- `GET /children/{id}/profile` y `GET /children/{id}/knowledge`, con token `family`.
- Pantalla `/familia/panel` con selector de niño, ficha del explorador y archipiélago.
- Separación de conceptos **fuertes** y **emergentes**.
- Estado vacío coherente para un niño recién creado.

**No entra** (excluido explícitamente por la HU, Bloque 2):

- Alertas o notificaciones proactivas.
- Informes exportables (PDF/email).
- Límites de tiempo o controles de uso.

**Tampoco entra, y es decisión de este brief:** el historial lección a lección. La HU pide
«actividad e historial», y su propia tabla de datos (Bloque 3) solo lista `ChildProfile`,
`knowledge_nodes` y sugerencias. El archipiélago **es** el historial: cada isla es un tema explorado,
con su materia y su maestría. Añadir un listado de lecciones exigiría decidir qué ve un adulto del
cuerpo de la lección, y eso es alcance nuevo, no este incremento.

**Mínimo entregable:** la familia abre el panel, elige un hijo y ve su ficha con conceptos fuertes y
emergentes; cambiar de hijo cambia los datos sin mezclarlos.

## Diseño

### Backend

Endpoints nuevos en `routers/children.py`, siguiendo el patrón que ya usan
`/children/{id}/login` y `/children/{id}/avatar/generate`:

| Método | Ruta | Auth | Entrada | Salida | Códigos |
|---|---|---|---|---|---|
| GET | `/children/{child_id}/profile` | `[FAMILIA]` | — | `ChildProfile` | `200` · `401` token `child` · `404` de otra familia |
| GET | `/children/{child_id}/knowledge` | `[FAMILIA]` | — | `list[KnowledgeNodeRead]` | `200` · `401` · `404` |

- **Reutiliza** los esquemas `ChildProfile` y `KnowledgeNodeRead` que ya existen. No se crean
  esquemas nuevos.
- Extraer a `services/child_service.py` un `build_profile(db, child) -> ChildProfile`, y hacer que
  `GET /me/profile` lo use también. La lógica de perfil deja de estar duplicada.
- La resolución del niño repite el patrón ya presente en `generate_child_avatar`: `db.get(Child, id)`
  y, si es `None` **o** `child.family_id != user.family_id`, **404**.

### Frontend

- Pantalla nueva `screens/FamilyPanel.tsx`, ruta `/familia/panel` dentro de `ProtectedRoute`.
- Cliente: añadir `getChildProfile(id)` y `getChildKnowledge(id)` a `api/children.ts`.
- Enlace de entrada desde `WhoExplores`, junto a los de IA y cuentos.
- Selector de niño: lista de botones si hay más de uno; si hay exactamente uno se selecciona solo.
- Claves i18n nuevas, **en español e inglés**:
  `panel.link`, `panel.title`, `panel.subtitle`, `panel.pick`, `panel.strong`, `panel.emerging`,
  `panel.emptyChild`, `panel.islandsCount`, `panel.error`.

### Datos

**Sin migración.** Todo sale de tablas y columnas existentes.

## Reglas de negocio

- **Fuerte vs emergente se deriva de `mastery`**, y el corte no es arbitrario: `ensure_node` crea la
  isla con `mastery = 1` al encender la chispa, y `upsert_node` la incrementa **solo** cuando el niño
  acierta el reto ([`knowledge.py:7-22`](../../../backend/app/repositories/knowledge.py#L7-L22)).
  Por tanto:
  - `mastery >= 2` → **fuerte**: lo exploró y además demostró que lo recuerda.
  - `mastery == 1` → **emergente**: lo exploró, todavía no lo ha demostrado.
- `islands` es derivado (número de `knowledge_nodes`), nunca una columna.
- **Aislamiento:** la familia solo ve a sus niños. Acceso a un niño ajeno → **404**, nunca 403, para
  no confirmar que existe.
- **JWT tipado:** estos endpoints son de familia. Un token `child` debe dar **401**.
- El selector no puede mezclar datos entre hermanos: al cambiar de niño se recargan ambas llamadas.

## Validación

| Caso | Dado / Cuando / Entonces | Test previsto |
|---|---|---|
| Camino feliz (perfil) | **Dado** familia autenticada con un hijo **Cuando** pido `GET /children/{id}/profile` **Entonces** 200 con nombre, edad e islas | `test_family_panel.py::test_family_reads_child_profile` |
| Camino feliz (ficha) | **Dado** un hijo con islas **Cuando** pido `GET /children/{id}/knowledge` **Entonces** 200 con sus nodos y su `mastery` | `test_family_panel.py::test_family_reads_child_knowledge` |
| Aislamiento | **Dado** un niño de **otra** familia **Cuando** pido su perfil o su ficha **Entonces** 404 | `test_family_panel.py::test_child_from_another_family_returns_404` |
| Token cruzado | **Dado** un token `child` **Cuando** llamo a estos endpoints **Entonces** 401 | `test_family_panel.py::test_child_token_rejected` |
| Niño sin actividad | **Dado** un hijo recién creado **Cuando** abro su ficha **Entonces** `islands = 0` y lista vacía, sin error | `test_family_panel.py::test_child_without_activity_is_coherent` |
| Selector | **Dado** dos hijos **Cuando** cambio de niño en el panel **Entonces** se muestran los datos del seleccionado | `FamilyPanel.test.tsx` |
| Fuertes/emergentes | **Dado** islas con `mastery` 1 y 3 **Cuando** abro el panel **Entonces** se separan en emergentes y fuertes | `FamilyPanel.test.tsx` |

## Trazabilidad

- **HU:** US5/US6 · **RF:** `RF-PLT-01`, `RF-SEG-02`
- **Pantallas:** `FamilyPanel.tsx` (nueva), `WhoExplores.tsx` (enlace)
- **Endpoints:** `GET /children/{id}/profile`, `GET /children/{id}/knowledge` (nuevos)
- **Tests:** `test_family_panel.py`, `FamilyPanel.test.tsx`
- **Documentos a actualizar en el mismo commit:** `contratos-api.md` (endpoints nuevos),
  `requisitos.md` (RF-PLT-01: corregir que se sirve desde `/children/{id}/*`, no desde `/me/*`),
  matriz de trazabilidad Parte 3.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Duplicar la lógica de perfil entre `/me/profile` y el endpoint de familia | Extraer `build_profile` y que ambos lo usen |
| Que el corte fuerte/emergente parezca arbitrario ante el evaluador | Se justifica en el modelo de datos: solo el reto acertado sube `mastery` |
| Filtrar datos entre hermanos al cambiar de selector | Recargar ambas llamadas al cambiar; test de selector |
| Tentación de mostrar el cuerpo de las lecciones al adulto | Fuera de alcance, declarado arriba |
