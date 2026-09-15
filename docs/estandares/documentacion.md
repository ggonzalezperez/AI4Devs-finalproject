# Estándares de documentación — Chispa ✨

> Cuelga de [estándares base](base.md). Define qué documento manda sobre qué, y cuándo hay que
> tocarlo.

---

## 1. Mapa: qué vive dónde

| Documento | Es la verdad sobre… | Se toca cuando… |
|---|---|---|
| `docs/estandares/` | Cómo se trabaja en el proyecto | Cambia una convención o se añade una skill |
| `docs/entrega-1/01-product/` | Qué se construye y por qué (HU, RF, alcance) | Cambia el alcance o una regla de negocio |
| `docs/entrega-1/02-technical-design/` | Cómo está construido (arquitectura, datos, API, seguridad) | Cambia un endpoint, una entidad o una decisión |
| `docs/entrega-1/02-technical-design/adr/` | Por qué se decidió así | Se toma una decisión estructural |
| `docs/entrega-1/03-testing/` | Cómo se valida | Cambia la estrategia o se añade un caso de aceptación |
| `docs/entrega-1/05-ai-log/` | Cómo se usó la IA | En cada tarea (bitácora) |
| `docs/entrega-2/` | Estado real de implementación y evidencias | En cada tarea completada |
| `README.md` | Cómo arrancar y qué hace la app | Cambia la puesta en marcha o una capacidad visible |
| `.superpowers/sdd/` | Qué se pidió y qué se entregó, tarea a tarea | En cada tarea |

## 2. Tiempo verbal: la trampa de esta entrega

`docs/entrega-1/` se escribió **antes** de implementar y está en futuro ("el sistema deberá"). Es
correcto para lo que era: una propuesta.

A partir de la Entrega 2 conviven dos registros y **no deben mezclarse**:

- `docs/entrega-1/` conserva el futuro. Es el documento de propuesta, y reescribirlo en presente
  borraría la evidencia de que hubo diseño previo a la implementación, que es justo lo que la guía
  valora.
- `docs/entrega-2/` se escribe en **presente y pasado**, y declara el estado real: qué se construyó,
  qué se verificó, qué se decidió no hacer y por qué.

Cuando el código y `entrega-1` discrepen, **no se edita el pasado en silencio**: se registra la
divergencia en `docs/entrega-2/` con su motivo. Un requisito que cambió es información valiosa; un
requisito reescrito a posteriori para que cuadre es falsificación.

## 3. ADR

Una decisión merece ADR cuando es **estructural y costosa de revertir**: elección de mecanismo de
auth, de estrategia de cifrado, de modelo de conversación, de política de migraciones.

Formato, siguiendo las siete ADR existentes:

```markdown
# ADR-00X — <decisión en una frase>

## Contexto
Qué problema había y qué restricciones aplicaban.

## Decisión
Qué se decidió, en presente.

## Alternativas consideradas
Qué más se valoró y por qué se descartó. Sin esto, la ADR no vale.

## Consecuencias
Qué gana y qué cuesta. Incluir lo que cuesta, siempre.
```

Numeración correlativa, nunca se reescribe una ADR aceptada: si se cambia de opinión, se escribe una
nueva que la supersede.

## 4. Trazabilidad

La cadena `HU → RF → endpoint/pantalla → test → evidencia` vive en la Parte 3 de
[`requisitos.md`](../entrega-1/01-product/requisitos.md).

Si una tarea añade o cambia una capacidad, la matriz se actualiza **en el mismo commit**. Una matriz
que apunta a un test inexistente es peor que no tener matriz: promete una verificación que nadie
hizo.

## 5. Bitácora de IA

La guía académica exige registrar prompts, herramientas, validación de salidas y **correcciones de
alucinaciones**. Vive en `docs/entrega-1/05-ai-log/`.

Formato de entrada, heredado del patrón de `AI4Devs-tdd-2604/prompts.md`: cada prompt se registra
con **su resultado real** debajo, no con lo que se esperaba que hiciera. Las correcciones manuales
sobre la salida de la IA son la parte más valiosa del registro, no una vergüenza que ocultar.

Lo gestiona la skill `chispa-bitacora`.

## 6. Estilo

- Español, segunda persona o impersonal. Sin "nosotros" corporativo.
- Tablas para lo comparable, prosa para lo que tiene matices. Una tabla de tres columnas con frases
  largas dentro es prosa mal maquetada.
- Enlaces relativos entre documentos, siempre. Un enlace roto es deuda.
- Bloques de código con lenguaje declarado y **comandos reales**, copiables tal cual.
- Nada de adjetivos de folleto ("robusto", "potente", "de vanguardia"). Si algo es rápido, dar el
  número.
