---
name: chispa-verificar
description: Ejecuta la cadena de verificación obligatoria de Chispa tras implementar — tests dirigidos, suite completa, linters, migraciones, curl real contra los endpoints, E2E con Playwright y capturas — y escribe el informe con las evidencias. Úsala al terminar cualquier implementación, y cuando el usuario diga "verifica", "comprueba que funciona" o "genera las evidencias".
---

# chispa-verificar

Ejecuta la cadena completa de [`docs/estandares/verificacion.md`](../../../docs/estandares/verificacion.md)
y deja el informe escrito.

**La regla que lo gobierna todo: ejecutas tú los comandos.** Nunca pidas a la persona usuaria que
corra los tests o que pruebe la pantalla. Si algo no puedes ejecutar (Docker parado, falta una
clave), dilo explícitamente y sigue con el resto; no lo des por bueno.

## Paso 1 — Tests dirigidos

Los del módulo tocado, para ciclo corto.

```bash
cd backend  && ./.venv/Scripts/python.exe -m pytest tests/test_<modulo>.py -v
cd frontend && npx vitest run src/<ruta>/<Fichero>.test.tsx
```

## Paso 2 — Suite completa y linters

```bash
cd backend  && ./.venv/Scripts/python.exe -m pytest -q
cd backend  && ./.venv/Scripts/python.exe -m ruff check .
cd frontend && npm test
cd frontend && npm run lint
```

Anota los **totales reales**. "108 passed", no "todo verde".

## Paso 3 — Base de datos (si hubo migración o cambio de modelo)

```bash
cd backend && ./.venv/Scripts/python.exe -m alembic upgrade head
cd backend && ./.venv/Scripts/python.exe -m alembic downgrade -1
cd backend && ./.venv/Scripts/python.exe -m alembic upgrade head
```

Anota la revisión antes y después. Si los tests dejaron datos, restaura y documenta la restauración.

## Paso 4 — Endpoints con `curl`

Levanta la app si hace falta (dev o Docker) y prueba **de verdad** cada endpoint nuevo o modificado.

Obtén primero los tokens reales, del tipo correcto:

```bash
# Token de familia
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo","email":"demo@chispa.test","password":"ChispaDemo2026!"}'

# Token de niño (requiere token de familia)
curl -s -X POST http://localhost:8000/children/1/login \
  -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN_FAMILIA>" \
  -d '{"pin":"1234"}'
```

Para cada endpoint, probar como mínimo:

| Caso | Por qué |
|---|---|
| Camino feliz | Código **y** forma del cuerpo |
| Token del tipo contrario | Debe dar 401 |
| Recurso de otra familia u otro niño | Debe dar 404, nunca 403 |
| Entrada inválida o moderada | Debe dar 422 |

Si el endpoint escribe, **restaura el estado** después y documenta cómo.

Comprobación específica de Chispa, obligatoria en todo endpoint que devuelva una lección: confirmar
que la respuesta **no contiene** `quiz_correct_index` ni `quiz_explanation`.

## Paso 5 — E2E con Playwright (si hay pantalla)

1. Levanta la app y recorre el flujo real en el navegador.
2. Captura cada hito en `docs/entrega-2/evidencias/` con nombre ordenable:
   `e2-<nn>-<pantalla>.png`.
3. Revisa la consola del navegador y anota cualquier error.
4. Comprueba el ancho móvil además del escritorio: es una app de tablet y móvil de casa.

## Paso 6 — Informe

Escribe `.superpowers/sdd/reports/task-<id>-report.md` con la plantilla de
[`verificacion.md` §3](../../../docs/estandares/verificacion.md). Incluye los comandos exactos y los
números reales.

Después, añade una línea a `.superpowers/sdd/progress.md`.

## Paso 7 — Veredicto

Termina siempre con uno de estos, explícito:

- **PASA** — cadena completa en verde, evidencias guardadas.
- **PASA CON RESERVAS** — verde, pero algo no se pudo verificar; di exactamente qué y por qué.
- **FALLA** — algo está roto; di qué y dónde.

Si el veredicto no es PASA, **no** marques la tarea como completa en `progress.md`.

## Prohibido

- Decir "los tests pasan" sin haberlos ejecutado en esta sesión.
- Dar por buena una pantalla que no has abierto.
- Omitir un caso de error porque "es obvio que funciona".
- Marcar la tarea completa sin informe escrito.
