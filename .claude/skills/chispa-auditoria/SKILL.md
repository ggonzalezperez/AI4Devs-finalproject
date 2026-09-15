---
name: chispa-auditoria
description: Auditoría sistemática de calidad del código de Chispa por fases — seguridad, deriva documentación-código, código muerto, deuda técnica y buenas prácticas de las librerías — terminando en un plan de acción priorizado. Úsala en barridos previos a una entrega y cuando el usuario diga "audita el código", "revisa la deuda técnica" o "qué está flojo".
---

# chispa-auditoria

Auditoría transversal, no revisión de un diff. Para revisar un cambio concreto antes de fusionar,
usa `chispa-revision-adversaria`.

Adaptada de `code-auditing` (lidr-specboot) al stack real de Chispa.

## Fase 0 — Línea base

Antes de opinar, medir:

```bash
cd backend  && ./.venv/Scripts/python.exe -m pytest -q && ./.venv/Scripts/python.exe -m ruff check .
cd frontend && npm test && npm run lint
```

Anota los números de partida. Una auditoría que empieza sin línea base no puede demostrar que mejoró
nada.

## Fase 1 — Inventario

- Módulos de backend por capa (`routers`, `services`, `repositories`, `models`, `schemas`).
- Pantallas y componentes de frontend.
- Migraciones y su cadena.
- Dependencias declaradas en `pyproject.toml` y `package.json`.

## Fase 2 — Deriva entre documentación y código

**La fase más rentable en este proyecto**, porque `docs/entrega-1/` se escribió antes de implementar.

1. Cada endpoint de `contratos-api.md` → ¿existe, con la misma firma y los mismos códigos?
2. Cada RF de `requisitos.md` → ¿está implementado? ¿Se aplica en servidor o solo en cliente?
3. Cada test nombrado en la matriz de trazabilidad → ¿existe de verdad?
4. Cada entidad de `modelo-datos.md` → ¿coincide con el modelo y las migraciones?

Cruce útil para el punto 3:

```bash
grep -ohrE "test_[a-z_0-9]+\.py|[A-Za-z]+\.test\.tsx?" docs/ | sort -u
```

Hallazgos ya conocidos de este tipo: el PIN de `RF-ONB-03` validado solo en cliente, y
`POST /me/stories` sin la entrada que documenta `RF-CUE-01`.

## Fase 3 — Seguridad

Prioridad máxima, por el perfil de usuario:

- Fugas en serialización: `quiz_correct_index`, `quiz_explanation`, `pin_hash`, `password_hash`,
  `family_id`, claves cifradas.
- Aislamiento: ¿toda consulta filtra por `child_id` o `family_id`?
- Moderación: ¿cubre todas las entradas de texto del niño?
- Secretos: ¿algo fuera de `.env`? ¿`.gitignore` los cubre?
- SSRF en los endpoints que aceptan URL (imagen local).
- Manejo de excepciones que se traguen fallos en silencio y dejen estado a medias.

## Fase 4 — Código muerto y duplicación

- Imports, funciones y componentes sin uso.
- Claves i18n huérfanas, o usadas sin existir en el catálogo.
- Endpoints que nadie llama desde el frontend.
- Lógica repetida tres o más veces.

## Fase 5 — Buenas prácticas de librerías

Para FastAPI, SQLAlchemy 2, Pydantic v2, React 18 y Vite: contrastar el uso real con la
documentación oficial vigente (usa Context7 para consultarla, no la memoria). Buscar patrones
desaconsejados y APIs obsoletas.

Ya detectado en la suite: avisos de deprecación de Starlette (`HTTP_422_UNPROCESSABLE_ENTITY`,
`TestClient` con `httpx`).

## Fase 6 — Plan de acción

Salida en tabla, ordenada por impacto y no por orden de descubrimiento:

```markdown
| # | Severidad | Área | Hallazgo | Evidencia | Acción | Coste |
|---|---|---|---|---|---|---|
```

Severidades: **Crítico** (seguridad del menor o pérdida de datos) · **Alto** (bug o deriva que rompe
un requisito) · **Medio** (deuda que costará) · **Bajo** (cosmético).

Cierra con las tres acciones de mayor relación valor/coste, nombradas y estimadas.

## Reglas

- Cada hallazgo, con su `fichero:línea`. Sin referencia, no es un hallazgo: es una impresión.
- No proponer reescrituras grandes: en este proyecto el tiempo es el recurso escaso.
- Distinguir lo que **está roto** de lo que **no te gusta**. Solo lo primero es severidad alta.
