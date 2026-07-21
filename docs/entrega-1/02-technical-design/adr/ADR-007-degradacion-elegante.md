# ADR-007 — Degradación elegante transversal

**Estado:** Aceptada (fase de diseño)

## Contexto

Chispa combina capacidades "de lujo" (imagen generada, voz, QR) con un núcleo imprescindible (leer la lección y hacer el quiz). En un entorno autoalojado y en manos de un niño, cualquiera de esos extras puede fallar: no hay clave de imagen, el navegador no soporta síntesis de voz, el proveedor tarda, la entrada es inapropiada. Nada de esto debe romper la experiencia base.

## Decisión

Aplicar **degradación elegante como principio transversal**, no como parche puntual:

- **Moderación de entrada (D6)**: una blocklist rechazará entradas inapropiadas con **422** y el mensaje amable *"Esta la vemos con un adulto"* 🛟, en lugar de generar contenido dudoso.
- **Imagen best-effort**: la función `_attach_image` del servicio de lecciones tragará las excepciones; si no hay imagen, la lección seguirá perfectamente (ver ADR-001).
- **Stub por defecto sin coste**: sin config de IA, el stub determinista responderá sin conexión ni gasto.
- **Voz / QR degradan**: si el navegador no soporta síntesis de voz o la API de QR, la funcionalidad se ocultará o desactivará sin romper la pantalla.

## Alternativas consideradas

- **Tratar los extras como obligatorios** (fallar si no hay imagen/voz/clave): frágil y frustrante; el niño vería errores por capacidades secundarias.
- **Ocultar los fallos sin señal alguna**: cómodo pero puede enmascarar problemas (mitigado con la recomendación de logging de ADR-001).

## Consecuencias

- **Experiencia base siempre disponible**: leer y aprender funcionará aunque fallen los extras.
- **Seguridad y calidez** ante entradas inapropiadas: mensaje de contención en lugar de error técnico.
- Coherencia con ADR-001 (fallback de IA) y ADR-003 (cifrado que degrada al stub ante error de clave).

## Componentes de diseño

- Servicio de lecciones (moderación D6, `_attach_image` best-effort).
- Servicios de proveedores de IA e imagen (stub por defecto).
- Frontend (síntesis de voz y `qrcode.react` con detección de soporte).
- Corresponde a los requisitos D6 y siguientes.
