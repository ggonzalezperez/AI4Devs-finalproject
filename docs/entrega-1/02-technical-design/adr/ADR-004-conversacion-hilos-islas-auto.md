# ADR-004 — Conversación en hilos e islas de conocimiento automáticas

**Estado:** Aceptada (fase de diseño)

## Contexto

La curiosidad del niño es una conversación: una pregunta lleva a otra. Cada lección debe poder encadenarse con la anterior (seguir el hilo) y, además, materializar el progreso en un mapa de "islas de conocimiento" que el niño pueda reabrir. Hay que decidir cómo modelar el hilo y cuándo nace una isla.

## Decisión

- **Hilos de conversación** sobre la propia tabla de lecciones: `lessons.parent_id` y `lessons.root_id` (auto-referencia lógica) enlazarán cada lección con su predecesora y con la raíz del hilo. Reabrir una isla = reabrir su chat.
- **Islas automáticas**: la `KnowledgeNode` se creará **al crear la lección**, desacoplada del quiz (`ensure_node`). `ensure_node` **no subirá maestría**; solo el **quiz correcto** la incrementará vía `upsert_node`. La maestría por defecto será `1`.

La opción alternativa —crear la isla al responder el quiz— dejaría sin isla las lecciones exploradas pero no evaluadas. Por eso el diseño desacopla la creación de la isla del acierto del quiz: responder mal **no** dejará de crear la isla, solo **no subirá** la maestría. Esta invariante se cubrirá con una prueba del tipo "responder mal no incrementa la maestría".

## Alternativas consideradas

- **Tabla de mensajes separada** para la conversación: duplicaría el contenido (cada lección ya es un turno) y complicaría el enlace lección↔isla; la auto-referencia en `lessons` es más simple y suficiente.
- **Crear la isla al responder el quiz** (opción descartada): dejaría sin isla las lecciones exploradas pero no evaluadas, perdiendo parte del mapa de curiosidad.

## Consecuencias

- **Reabrir una isla reabrirá su chat**: navegación coherente entre el mapa y la conversación.
- El mapa reflejará **todo lo explorado** (isla al crear), mientras que la **maestría** reflejará lo **demostrado** (solo quiz correcto).

## Componentes de diseño

- Modelos (`Lesson.parent_id` / `root_id`, `KnowledgeNode`, `mastery` default 1).
- Servicio de lecciones (`ensure_node`, `upsert_node`).
- Prueba prevista para la invariante "responder mal no incrementa la maestría".
