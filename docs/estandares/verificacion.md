# Estándares de verificación — Chispa ✨

> Cuelga de [estándares base](base.md). Adaptado de `lidr-specboot`
> (`docs/openspec-tasks-mandatory-steps.md`) al flujo SDD de Chispa.
>
> **Regla que lo gobierna todo:** el agente ejecuta él mismo cada verificación. **Nunca** se delega
> en la persona usuaria "prueba esto y dime". Una tarea no se marca completa hasta que el agente ha
> corrido los comandos y ha dejado el informe escrito.

---

## 1. Por qué esta cadena

La guía académica pide "evidencias del funcionamiento" como entregable. Si las evidencias se
fabrican al final, salen pobres y desactualizadas. Si cada tarea las produce como subproducto, la
entrega se escribe sola y además son ciertas.

## 2. Cadena obligatoria por tarea

Toda tarea de implementación recorre estos pasos **en orden**. Ninguno es opcional, ni siquiera
cuando el cambio "es pequeño".

### Paso 0 — Rama primero

Crear la rama antes de tocar un fichero. Nunca se implementa sobre `main`.

```bash
git checkout -b <tipo>-<ambito-corto>
```

### Paso 1 — Test que falla (TDD)

Escribir el test **antes** que la implementación, y verlo fallar por la razón correcta. Un test que
pasa a la primera no ha probado nada.

`tdd-guard` aplica esta regla con hooks: intentar escribir implementación sin un test que falle
queda bloqueado. Si el hook bloquea, la respuesta correcta es escribir el test, no desactivar el hook.

### Paso 2 — Implementación mínima

Solo el código que hace pasar el test. Nada de anticipar requisitos futuros.

### Paso 3 — Tests dirigidos

Ejecutar primero los tests del módulo tocado, para ciclo corto:

```bash
# Backend
cd backend && ./.venv/Scripts/python.exe -m pytest tests/test_<modulo>.py -v

# Frontend
cd frontend && npx vitest run src/screens/<Pantalla>.test.tsx
```

### Paso 4 — Suite completa y linters

Antes de dar nada por hecho, la suite entera más los linters. Una regresión en otro módulo es tan
bloqueante como un test propio en rojo.

```bash
cd backend  && ./.venv/Scripts/python.exe -m pytest -q && ./.venv/Scripts/python.exe -m ruff check .
cd frontend && npm test && npm run lint
```

Registrar los totales: *"108 passed"*, no *"pasan los tests"*.

### Paso 5 — Estado de la base de datos

Para cualquier cambio que toque modelos o migraciones:

1. Anotar el estado previo relevante (conteos de las tablas afectadas, revisión actual de Alembic).
2. Aplicar y revertir la migración: `alembic upgrade head && alembic downgrade -1 && alembic upgrade head`.
3. Comprobar el estado posterior y confirmar que no quedan mutaciones no deseadas.
4. Si los tests dejaron datos, restaurarlos y documentar la restauración.

### Paso 6 — Prueba manual de endpoints con `curl`

**El agente ejecuta los `curl`.** Para cada endpoint nuevo o modificado:

- El camino feliz, comprobando código de estado **y** forma del cuerpo.
- Los casos de error que el requisito promete: 401 por token cruzado, 404 por acceso ajeno, 422 por
  validación o moderación, 409 donde aplique.
- Si el endpoint crea, actualiza o borra, **restaurar el estado** después y documentar cómo.

Toda petición autenticada lleva su token del tipo correcto. Probar un endpoint de niño con token de
familia (y esperar 401) es parte de la evidencia, no un descuido.

### Paso 7 — E2E con Playwright (si hay pantalla)

Recorrer el flujo real en el navegador contra la app levantada, y capturar pantalla de cada hito.
Las capturas van a `docs/entrega-2/evidencias/` con nombre estable y ordenable
(`e2-07-panel-familia.png`).

Comprobar además que la consola del navegador queda sin errores.

### Paso 8 — Documentación

Actualizar en el **mismo commit**:

- La matriz de trazabilidad de [`requisitos.md`](../entrega-1/01-product/requisitos.md) si cambió
  alguna capacidad.
- [`contratos-api.md`](../entrega-1/02-technical-design/contratos-api.md) si cambió algún endpoint.
- Una ADR si se tomó una decisión estructural.
- La bitácora de IA (`chispa-bitacora`).

Un cambio funcional cuya documentación se actualiza "después" es un cambio incompleto.

### Paso 9 — Informe

Escribir el informe en `.superpowers/sdd/reports/task-<id>-report.md` con la plantilla de abajo.
**La tarea no se marca completa en `progress.md` hasta que el informe existe.**

## 3. Plantilla de informe

```markdown
# Informe — <id de tarea>

- Fecha: AAAA-MM-DD
- Rama: <rama>
- HU / RF cubiertos: <US…, RF-…>

## Comandos ejecutados
- `<comando 1>`
- `<comando 2>`

## Resultado de tests
- Dirigidos: X passed, Y failed
- Suite backend: X passed · ruff: limpio
- Suite frontend: X passed · tsc: limpio
- Duración: <tiempo>

## Estado de base de datos
- Revisión Alembic antes / después: <rev> → <rev>
- upgrade/downgrade/upgrade: OK / FALLO
- Estado restaurado: sí / no · acciones: <…>

## Endpoints probados (curl)
| Método y ruta | Caso | Esperado | Obtenido |
|---|---|---|---|
| `POST /…` | camino feliz | 201 | 201 |
| `POST /…` | token cruzado | 401 | 401 |

## E2E
- Flujo recorrido: <…>
- Capturas: `docs/entrega-2/evidencias/<…>.png`
- Consola del navegador: sin errores / <errores>

## Documentación actualizada
- <ficheros>

## Resultado
- Estado: PASA / FALLA
- Bloqueantes: ninguno / <lista>
```

## 4. Revisión adversaria antes de fusionar

Cuando la cadena termina en PASA, **antes de fusionar** se ejecuta
`chispa-revision-adversaria`, en sesión distinta de la que implementó. Su cometido no es confirmar
que funciona, sino intentar demostrar que no.

Severidades y qué implican:

| Severidad | Significado | ¿Bloquea la fusión? |
|---|---|---|
| **Bloqueante** | Comportamiento incorrecto, fallo de seguridad o violación del requisito | Sí |
| **Mayor** | Bug probable o hueco relevante | Sí, hasta corregir o actualizar el requisito |
| **Menor** | Claridad o mantenibilidad | No, se anota |
| **Pregunta** | Necesita confirmación humana | Se resuelve antes de fusionar |

Cada hallazgo indica dónde va el arreglo: **código**, **tests**, **documentación** o **requisito**.

## 5. Lista de comprobación final

Antes de considerar hecha una tarea:

- [ ] Rama propia, creada antes de implementar
- [ ] Test escrito antes que el código, y visto fallar
- [ ] Suite completa en verde, backend y frontend
- [ ] `ruff check .` y `tsc --noEmit` limpios
- [ ] Migración reversible, probada en SQLite y Postgres
- [ ] Endpoints probados con `curl`, incluidos los casos de error prometidos
- [ ] E2E recorrido y capturas guardadas (si hay pantalla)
- [ ] Trazabilidad HU → RF → endpoint → test → evidencia actualizada
- [ ] Bitácora de IA actualizada
- [ ] Informe escrito en `reports/`
- [ ] Revisión adversaria ejecutada, sin bloqueantes ni mayores abiertos
- [ ] Sin secretos en el diff
