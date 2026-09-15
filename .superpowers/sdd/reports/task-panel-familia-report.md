# Informe — panel-familia

- Fecha: 2026-09-14
- Rama: `entrega_2`
- HU / RF cubiertos: US5/US6 · `RF-PLT-01`, `RF-SEG-02`

## Comandos ejecutados

```bash
cd backend  && ./.venv/Scripts/python.exe -m pytest -q
cd backend  && ./.venv/Scripts/python.exe -m ruff check .
cd frontend && npm test
cd frontend && npm run lint
```

## Resultado de tests

- Dirigidos: `test_family_panel.py` 5 passed · `FamilyPanel.test.tsx` 2 passed · `children.test.ts` 2 passed
- Suite backend: **127 passed** (eran 108 al empezar la jornada) · `ruff`: limpio
- Suite frontend: **52 passed** en 29 ficheros (eran 48 en 27) · `tsc --noEmit`: limpio
- Avisos: 1 (migración pendiente a `httpx2`, decisión documentada)

## Estado de base de datos

- **Sin migración.** El panel no añade entidades ni columnas: todo sale de `children` y
  `knowledge_nodes`, que ya existían.
- Revisión de Alembic sin cambios: `ad23d09d1b34` (HEAD) antes y después.
- Datos de demo creados en la base de desarrollo (SQLite) para las capturas; no afectan a los tests,
  que usan SQLite en memoria y esquema limpio por test.

## Endpoints probados (curl)

Contra `uvicorn` real, no contra el cliente de pruebas.

| Método y ruta | Caso | Esperado | Obtenido |
|---|---|---|---|
| `GET /children/{id}/profile` | camino feliz | 200 + `{name, age, islands}` | 200 · `{"name":"Nora","age":8,"islands":1,...}` |
| `GET /children/{id}/knowledge` | camino feliz | 200 + nodos con `mastery` | 200 · `mastery: 2` tras acertar el reto |
| `GET /children/{id}/profile` | token `child` | 401 | 401 |
| `GET /children/{id}/knowledge` | sin token | 401 | 401 |
| `GET /children/99999/profile` | niño ajeno/inexistente | 404 | 404 |
| `POST /children` | PIN `"12a4"` | 422 | 422 |
| `POST /lessons` | curiosidad «armadura» | 201 (no bloquear) | 201 |
| `GET /lessons/{id}` | fuga del quiz | 0 apariciones | 0 apariciones de `quiz_correct_index`/`quiz_explanation` |

Estado restaurado: no aplica; solo se crearon datos de demo en la base de desarrollo.

> **Incidencia durante la verificación:** el primer intento de `curl` falló con 422 al registrar.
> No era la app: `email-validator` rechaza el TLD `.test` por reservado, y mi dato de prueba lo
> usaba. Corregido el dato, no el código.

## E2E

- Flujo recorrido: login de familia → tripulación → «Ver el aprendizaje» → ficha de Nora →
  selector a Leo → vuelta a Nora en ancho móvil (390 px).
- Capturas en `docs/entrega-2/evidencias/`:
  - `e2-01-familia-tripulacion.png`
  - `e2-02-panel-familia-nora.png` — 2 conceptos dominados, 1 emergente
  - `e2-03-panel-familia-leo-sin-actividad.png` — estado vacío coherente (caso límite 2 de la HU)
  - `e2-04-panel-familia-movil.png`
- Consola del navegador: **0 errores**. Quedan 2 avisos de *future flags* de React Router v6→v7,
  preexistentes y ajenos a este cambio.
- Verificado en vivo que el selector no mezcla hermanos: al pasar a Leo desaparecen las islas de
  Nora y aparece `0 islas exploradas`.

## Documentación actualizada

- `docs/entrega-1/02-technical-design/contratos-api.md` — dos endpoints nuevos y el 502 del avatar
- `docs/entrega-1/01-product/requisitos.md` — `RF-PLT-01` reescrito (entradas, reglas y Tabla B)
- `docs/entrega-1/01-product/historias-usuario.md` — US5/US6: corregido el supuesto de `/me/*`
- `.superpowers/sdd/briefs/task-panel-familia-brief.md`

## Decisiones tomadas durante la implementación

1. **El panel no puede servirse desde `/me/*`.** Esos endpoints exigen token `child` por diseño
   (ADR-002). Dar acceso a la familia habría roto el JWT tipado, que es una garantía de seguridad,
   así que se corrigió la HU y se crearon endpoints propios de familia.
2. **El corte fuerte/emergente sale del modelo de datos, no de una heurística.** La isla nace con
   `mastery = 1` y solo sube al acertar el reto, así que `mastery >= 2` significa literalmente «lo
   exploró y demostró que lo recuerda».
3. **`build_profile` extraído a `child_service`** para que el niño y su familia vean exactamente la
   misma ficha. Estaba duplicado en dos routers.
4. **El historial lección a lección queda fuera**, declarado en el brief: exigiría decidir qué ve un
   adulto del cuerpo de la lección, y eso es alcance nuevo.

## Resultado

- Estado: **PASA**
- Bloqueantes: ninguno
- US5/US6 era la única historia del MVP sin implementar. Con esto, las 10 historias están cubiertas.
