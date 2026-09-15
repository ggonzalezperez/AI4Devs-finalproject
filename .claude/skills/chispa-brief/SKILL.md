---
name: chispa-brief
description: Convierte una historia de usuario, un requisito (RF) o una idea suelta en un brief ejecutable de Chispa, con alcance cerrado, criterios de validación y trazabilidad. Úsala ANTES de implementar cualquier cosa, y cuando el usuario diga "vamos a hacer X", "prepara el brief de X" o describa una funcionalidad nueva.
---

# chispa-brief

Convierte una petición en un **brief ejecutable**: un documento del que otra sesión pueda
implementar sin volver a preguntar nada.

Adaptado de `enrich-us` (lidr-specboot) al flujo SDD de Chispa.

## Cuándo

- Antes de tocar código, siempre.
- Cuando una HU de `docs/entrega-1/01-product/historias-usuario.md` entra en implementación.
- Cuando aparece una petición nueva que no está en las HU (entonces el brief incluye además la
  decisión de si amplía el alcance o no).

## Paso 1 — Reunir el contexto real

No inventar. Leer, en este orden:

1. La HU en `docs/entrega-1/01-product/historias-usuario.md` (plantilla DoR de 6 bloques).
2. Los RF que la realizan en `docs/entrega-1/01-product/requisitos.md` (Tabla A de la Parte 3).
3. Los contratos afectados en `docs/entrega-1/02-technical-design/contratos-api.md`.
4. **El código que ya existe.** Qué hay construido, qué se reutiliza y qué falta de verdad.

Si el documento y el código discrepan, anotarlo: es un hallazgo, y el brief debe decidir cuál de los
dos se corrige.

## Paso 2 — Cerrar el alcance

Un brief sin fronteras produce implementaciones infinitas. Declarar explícitamente:

- **Entra:** la lista corta de lo que se construye.
- **No entra:** lo que alguien podría asumir razonablemente y **no** se va a hacer.
- **Mínimo entregable:** la frase que define "hecho".

## Paso 3 — Escribir el brief

Guardar en `.superpowers/sdd/briefs/task-<id>-brief.md`:

```markdown
# Brief — <id>: <título>

## Contexto
Por qué existe esta tarea. HU y RF que la motivan.

## Alcance
- Entra: …
- No entra: …
- Mínimo entregable: …

## Diseño
- Backend: capas tocadas, endpoints (método, ruta, auth, entrada, salida, códigos).
- Frontend: pantallas, rutas, componentes, claves i18n nuevas.
- Datos: entidades y migración (siempre aditiva).

## Reglas de negocio
Las que el implementador no puede deducir del código.
Incluir SIEMPRE las que toquen seguridad del menor.

## Validación
| Caso | Dado / Cuando / Entonces | Test previsto |
|---|---|---|
| Camino feliz | … | `test_…` |
| Error esperado | … | `test_…` |
| Acceso cruzado | … | `test_…` |

## Trazabilidad
HU: US… · RF: RF-… · Pantallas: … · Endpoints: … · Tests: …

## Riesgos
Qué puede salir mal y qué lo mitiga.
```

## Paso 4 — Comprobar antes de entregar el brief

- [ ] Todo endpoint lleva método, ruta, tipo de token, entrada, salida y códigos de error
- [ ] Toda entrada del niño declara su moderación y su 422
- [ ] Todo acceso a datos declara su aislamiento (404 cruzado)
- [ ] Hay al menos un caso negativo por cada regla de seguridad tocada
- [ ] La migración, si la hay, es aditiva y reversible
- [ ] Las claves i18n nuevas están en español **e** inglés
- [ ] Cada criterio de validación nombra el test que lo probará

## Reglas

- Si falta información para cerrar el alcance, **preguntar** antes de escribir el brief. Un brief con
  huecos se paga tres veces durante la implementación.
- No copiar la HU: el brief es más concreto y habla de ficheros, no de intenciones.
- El brief lo escribe una sesión y lo implementa otra. Escribirlo pensando en ese lector.
