# ADR-001 — Seams de IA con fábrica por familia y fallback al stub

**Estado:** Aceptada (fase de diseño)

## Contexto

Chispa genera lecciones e imágenes con IA, pero debe funcionar en muchos escenarios: familias con clave de Claude, familias que solo quieren IA local (Ollama), familias sin IA, y momentos en que el proveedor falla o tarda. Sobre todo, **el niño nunca debe ver un fallo del proveedor** en mitad de su curiosidad.

## Decisión

Definir **dos seams** (patrón puerto/adaptador), uno para texto y otro para imagen, con una **fábrica que elegirá el adaptador según la config de la familia** y **caerá a un stub** cuando no haya clave o el proveedor sea desconocido:

- **Texto**: puerto `LessonGenerator` (Protocol) y fábrica `build_generator(config)`. Adaptadores previstos: `ClaudeGenerator`, `OllamaGenerator`, `OpenAICompatGenerator`, `GeminiGenerator`, y `StubLessonGenerator` como fallback determinista.
- **Imagen**: puerto `ImageGenerator` (Protocol) y fábrica `build_image_generator(config)`. Adaptador de reserva `StubImageGenerator` (devolverá `None`).

Todos los adaptadores usarán `httpx` **sin SDKs**, con prompting y parseo compartidos (que validarán exactamente 3 opciones y `0 ≤ correct_index < 3`) y timeout de 120 s.

## Alternativas consideradas

- **Llamar a los SDKs de cada proveedor directamente**: acopla la lógica de negocio a cada vendor (lock-in) y multiplica dependencias.
- **Sin fallback**: cualquier caída del proveedor rompería la experiencia y el niño vería un error.

## Consecuencias

- Permitirá proveedores **enchufables** por config; cambiar de vendor no tocará la lógica de negocio (sin lock-in).
- *El niño nunca verá un fallo del proveedor*: ante falta de clave, proveedor desconocido o error, se usará el stub.
- **Concern operacional**: el fallback silencioso podrá **ocultar errores** de configuración/proveedor. Por ello se prevé **añadir logging** cuando se caiga al stub por error (no solo por ausencia de config), para observabilidad.

## Componentes de diseño

- Servicio de proveedores de IA (`build_generator`, adaptadores, `_parse_lesson`).
- Servicio de proveedores de imagen (`build_image_generator`).
- Módulo del puerto de lecciones (`LessonGenerator` y `StubLessonGenerator`).
- Módulo del puerto de imagen (`ImageGenerator`).
