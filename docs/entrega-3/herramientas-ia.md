# Herramientas de IA usadas en Chispa

> Inventario de las **skills**, **agentes** y **automatismos** con los que se construyó el producto:
> qué hace cada uno, de dónde viene y dónde vive en este repositorio. Complementa la bitácora de
> prompts de [`docs/entrega-1/05-ai-log/`](../entrega-1/05-ai-log/prompts.md), que registra el *qué se
> pidió*; esto registra el *con qué*.

## 1. El principio

Las tres actividades que no deben mezclarse son **especificar**, **implementar** y **revisar**. La
regla de trabajo fue que **quien revisa no sea quien implementa**, porque una sesión que acaba de
escribir un código es el peor juez de ese código: ya ha decidido que está bien.

Todo lo que sigue existe para sostener esa separación, o para que el criterio humano entre en el
momento correcto.

## 2. Skills propias del proyecto

Viven en [`.claude/skills/`](../../.claude/skills/), versionadas con el código. Son seis, escritas
para este proyecto y en español, porque la entrega es en español.

| Skill | Qué hace | Cuándo se invoca |
|---|---|---|
| [`chispa-brief`](../../.claude/skills/chispa-brief/SKILL.md) | Convierte una historia o una idea suelta en un **brief ejecutable**: alcance cerrado, diseño por capas, reglas de negocio, casos de validación con su test nombrado y trazabilidad HU↔RF | **Antes de tocar código, siempre** |
| [`chispa-verificar`](../../.claude/skills/chispa-verificar/SKILL.md) | Ejecuta la cadena de verificación completa —tests dirigidos, suite, linters, migraciones, `curl` real, E2E con capturas— y escribe el informe con **números reales** | Al terminar cualquier implementación |
| [`chispa-revision-adversaria`](../../.claude/skills/chispa-revision-adversaria/SKILL.md) | Revisión independiente que **intenta romper** lo implementado: deriva documentación↔código, casos negativos sin cubrir, fugas de seguridad del menor. Veredicto PASA/FALLA | Antes de fusionar |
| [`chispa-auditoria`](../../.claude/skills/chispa-auditoria/SKILL.md) | Barrido sistemático por fases: seguridad, deriva, código muerto, deuda técnica | Antes de una entrega |
| [`chispa-bitacora`](../../.claude/skills/chispa-bitacora/SKILL.md) | Registra prompts, resultado real, **alucinaciones detectadas** y correcciones humanas | Al cerrar una tarea |
| [`chispa-commit`](../../.claude/skills/chispa-commit/SKILL.md) | Commits en español siguiendo la convención del repositorio, **sin ninguna firma de herramienta** | Al cerrar una tarea verificada |

La más rentable fue `chispa-brief`. Un brief sin fronteras produce implementaciones infinitas, y
obligarse a escribir «qué **no** entra» antes de empezar ahorró más tiempo que cualquier otra cosa.

`chispa-verificar` tiene una regla que resultó decisiva: **la ejecuta la sesión, no la persona**.
«Los tests pasan» sin haberlos ejecutado en esa sesión está prohibido por escrito.

## 3. Skills de terceros

Del conjunto **Superpowers** (`obra/superpowers`), instalado como *plugin* y por tanto **fuera de este
repositorio**: son código de terceros y vendorizarlo aquí añadiría ruido y una cuestión de atribución.
Se listan las que dejaron rastro en la documentación del proyecto.

| Skill | Para qué se usó |
|---|---|
| `superpowers:brainstorming` | Explorar el producto antes de escribir nada, en las fases de definición |
| `superpowers:writing-plans` | Convertir la definición en planes por tareas (los «Plan 2/3/4» del libro mayor) |
| `superpowers:executing-plans` · `subagent-driven-development` | Ejecutar esos planes tarea a tarea, con puntos de revisión entre medias |
| `superpowers:test-driven-development` | Disciplina de test primero, rojo observado, implementación mínima |
| `superpowers:systematic-debugging` | Causa raíz antes que parche. Usada, por ejemplo, para el alta que falló en la demo publicada |
| `superpowers:requesting-code-review` · `receiving-code-review` | Pedir y encajar revisión de una sesión distinta a la que implementó |
| `superpowers:verification-before-completion` | No dar por terminado lo que no se ha comprobado |

Otras de uso puntual: `anthropic-skills:pdf` al generar el manual, y la skill `run` para levantar la
aplicación y conducirla en un navegador real.

> **Honestidad sobre este inventario.** Las skills de las sesiones antiguas están reconstruidas a
> partir de lo que quedó escrito en la documentación y en el libro mayor, no de un registro
> exhaustivo de invocaciones. Se listan las que dejaron rastro verificable.

## 4. Agentes

No hay agentes propios en `.claude/agents/`: los roles se materializaron **invocando skills en
sesiones separadas**, que es lo que de verdad garantiza la independencia. El catálogo de roles
previsto está en [`agentes.md`](../entrega-1/05-ai-log/agentes.md) y se cumplió así:

| Rol | Cómo se materializó |
|---|---|
| Planificador | `chispa-brief` en una sesión, antes de implementar |
| Implementador | Sesión distinta, ejecutando el brief con TDD |
| Revisor de conformidad | `chispa-revision-adversaria`, veredicto PASA/FALLA |
| Revisor de calidad | Revisión de código en sesión independiente |
| Depurador | `superpowers:systematic-debugging` |
| Documentalista | `chispa-bitacora` y las skills de documentación |

**Dónde falló la disciplina, y está declarado:** la verificación de la Entrega 2 la hizo la misma
sesión que implementó, no una independiente como exige el estándar propio. Queda anotado en
[`verificacion.md`](../entrega-2/verificacion.md) en lugar de disimularse.

## 5. Automatismos: TDD Guard

Lo único de esta lista que **no se puede ignorar**, porque no es una instrucción sino un *hook* que
bloquea la escritura.

Adaptado de [`nizos/tdd-guard`](https://github.com/nizos/tdd-guard), con reporteros conectados a
`pytest` y a `vitest`. Impide escribir implementación sin un test que falle antes, y **solo admite un
test nuevo por ciclo**, para que el rojo–verde–refactor no se convierta en escribir diez tests y
luego el código.

Bloqueó al asistente en varias ocasiones durante el desarrollo, registradas en la bitácora. En la
última jornada rechazó un intento de añadir dos tests a la vez, obligando a partirlo en dos ciclos.

La configuración está en [`frontend/vite.config.ts`](../../frontend/vite.config.ts) (reportero de
vitest) y en [`backend/pytest.ini.example`](../../backend/pytest.ini.example).

## 6. Estándares de proyecto

En [`docs/estandares/`](../estandares/base.md): base, backend, frontend, verificación y documentación.
Adaptados de `lidr-specboot`, traducidos y ajustados —el original impone *English Only*, incompatible
con una entrega en español—. Son el contrato que las skills aplican.

## 7. Qué no se usó, y por qué

- **Agentes en paralelo para implementar.** Se probaron para revisión, no para escribir código: dos
  sesiones tocando el mismo árbol producen conflictos que cuestan más de lo que ahorran.
- **Generación automática de commits.** La convención es en español y sin firmas de herramienta; los
  mensajes los redacta el asistente pero explicando **por qué**, no listando ficheros.
- **Cobertura como objetivo.** Ninguna skill persigue un porcentaje. La regla es que **cada regla de
  seguridad del menor tenga su caso negativo**, que es una medida de riesgo y no de líneas.
