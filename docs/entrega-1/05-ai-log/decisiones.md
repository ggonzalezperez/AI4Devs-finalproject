# Decisiones de IA (AI-LOG) — Chispa

> Uso previsto de IA · Entrega 1 · Máster LIDR–AI4Devs
> Este documento define **la bitácora de IA que se mantendrá** durante el desarrollo, en el
> formato de la guía §5.6. Cada entrada documentará el ciclo
> **revisión → corrección → decisión justificada**, que es la evidencia del uso estructurado
> y responsable de la IA.
>
> **Estado:** en la Entrega 1 (documental) todavía no hay código, así que la bitácora aún no
> tiene entradas reales. Aquí se fija el **formato**, se incluye **un ejemplo ilustrativo**
> claramente marcado como plantilla y se listan los **temas de decisión** que la bitácora
> cubrirá. El registro completo se irá rellenando durante las **Entregas 2 y 3**, a medida
> que cada tarea se implemente y revise.

## 1. Formato de cada entrada (guía §5.6)

Cada registro **AI-LOG-00X** seguirá esta plantilla:

- **Fecha** — de la interacción con IA (se anotará el commit como ancla verificable).
- **Objetivo** — qué se le pidió a la IA.
- **Herramienta/modelo** — Claude Code + skills empleadas; proveedor en runtime si aplica.
- **Entrada** — contexto suministrado (brief, PRD, restricciones).
- **Salida** — qué produjo la IA.
- **Validaciones** — tests, lint, revisión de spec/calidad, migración segura.
- **Problemas detectados** — errores o alucinaciones encontrados en la revisión.
- **Corrección** — cambio manual o ajuste aplicado.
- **Decisión** — aceptado / aceptado con hallazgo abierto / desviación justificada, y por qué.

## 2. Ejemplo ilustrativo (PLANTILLA — no es una decisión ya tomada)

> El siguiente registro es un **ejemplo de referencia** con el estilo del AI-LOG-007 de la
> guía §5.6. Sirve para mostrar el nivel de detalle esperado; **no** documenta una decisión
> real del proyecto. Las entradas reales se añadirán en las Entregas 2 y 3.

### AI-LOG-000 (ejemplo) — Costura de IA con fallback seguro (generador de lecciones)

- **Fecha:** *(se anotará cuando se implemente)* · commit *(SHA como ancla)*
- **Objetivo:** Enchufar un proveedor de IA real por familia sin que un fallo del proveedor
  llegue nunca al niño.
- **Herramienta/modelo:** Claude Code (skills `test-driven-development`,
  `subagent-driven-development`); proveedor en runtime configurable.
- **Entrada:** Brief de adaptadores HTTP + fábrica, y brief de cableado del servicio de
  lecciones a la config de familia con fallback.
- **Salida:** Una fábrica `build_generator(cfg)` que devuelve el adaptador configurado; el
  servicio intentaría `generator.generate(...)` y, ante **cualquier** excepción, caería a un
  `StubLessonGenerator` determinista.
- **Validaciones:** Tests dirigidos + suite completa en verde; `ruff` limpio; sin llamadas
  HTTP reales (mock con `monkeypatch`); además, una prueba funcional real contra el proveedor.
- **Problemas detectados:** *(ejemplo)* el `monkeypatch` de la fábrica no surtiría efecto si
  se invocara por ruta totalmente cualificada.
- **Corrección:** Importar la fábrica al **namespace del módulo** que la usa para que el
  parcheo de tests funcione.
- **Decisión:** **Aceptado.** El fallback silencioso hacia el stub sería deliberado: el niño
  nunca vería un error del proveedor (continuidad de la experiencia).

## 3. Temas de decisión que la bitácora cubrirá

Durante las Entregas 2 y 3 se prevé registrar, como mínimo, entradas AI-LOG para estas
decisiones de diseño (se listan como **temas a documentar**, no como hechos consumados):

| Tema previsto | Qué decisión de IA se registrará |
|---|---|
| **Costura de IA + fallback seguro** | Integrar el proveedor tras una interfaz (*seam*) con degradación a stub determinista si falla o no está configurado |
| **Conversación en hilos / grafo de conocimiento** | Cómo la lección se convierte en conversación con contexto y cómo/cuándo se crea la "isla" en el archipiélago |
| **Aprobación parental de cuentos** | Flujo aprobar/editar/rechazar; el rechazo debe conservar el texto original para trazabilidad |
| **Config de IA por familia con clave cifrada** | Cifrado de la clave de API (Fernet), sin almacenarla en claro; clave inválida ⇒ fallback seguro |
| **Recuperación de contraseña sin email** | Código de recuperación de un solo uso (solo se guarda su hash) y protección **anti-enumeración** de cuentas |
| **Mitigación de SSRF en endpoint de imagen local** | Validar la URL antes de cualquier petición saliente; permitir LAN/localhost (uso legítimo) y bloquear direcciones link-local |
| **Aislamiento entre familias** | Guards de token y filtrado por `family_id`; el niño solo ve contenido `approved` |
| **JWT tipado** | Separar y verificar el tipo de token (niño ↔ familia) para evitar escaladas de privilegio |
| **Validación funcional real (E2E)** | Contrastar la integración de IA e imagen contra un proveedor vivo, más allá de los mocks |
| **Hallazgos de calidad abiertos** | Registrar deuda técnica no bloqueante (p. ej. `except` genérico sin logging, opción de proveedor no ideal) como hallazgo documentado |

Cada uno de estos temas generará una o varias entradas con el formato de la sección 1,
reflejando el ciclo real de revisión y corrección cuando la tarea se implemente.
