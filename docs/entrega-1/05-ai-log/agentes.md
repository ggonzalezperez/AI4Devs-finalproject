# Agentes y roles de IA (previstos) — Chispa

> Uso previsto de IA · Entrega 1 · Máster LIDR–AI4Devs
> Catálogo de los **roles de subagente** que se emplearán para construir Chispa y para
> elaborar esta propia entrega documental. Mapeados a los "posibles subagentes" que sugiere
> la guía §6. Redactado en clave de plan: describe qué hará cada rol, no lo que ya hizo.

## 1. Principio rector

> "La función de estos agentes no debe ser sustituir el criterio humano, sino especializar
> las revisiones y reducir omisiones." — Guía §6

En Chispa los agentes **especializarán y separarán** las tres actividades que no deben
mezclarse: **especificar**, **implementar** y **revisar**. La clave del uso responsable será
que **quien revisa no sea quien implementa**: cada tarea recibirá un veredicto de conformidad
y otro de calidad emitidos por agentes distintos del ejecutor. El registro de esas decisiones
se llevará en [`decisiones.md`](decisiones.md).

## 2. Roles que se usarán en el desarrollo del producto

| Rol | Responsabilidad prevista |
|---|---|
| **Agente planificador (brief)** | Escribirá la spec ejecutable: archivos, código concreto, tests-primero, pasos ver-fallar/ver-pasar, commit local |
| **Agente implementador** | Ejecutará el brief al pie de la letra con TDD; correrá `ruff`/lint; generará migración no destructiva; se detendrá si hay drops/alters |
| **Agente revisor de conformidad (spec)** | Verificará requisito a requisito contra el diff; emitirá un veredicto **Spec compliance: PASS/FAIL** |
| **Agente revisor de calidad/seguridad** | Buscará deuda técnica, errores silenciosos, olores de código y riesgos de seguridad; emitirá un veredicto de calidad (aprobado / aprobado con hallazgos) |
| **Agente de depuración sistemática** | Aislará las causas de fallos (p. ej. por qué un test falla en jsdom) antes de tocar código |
| **Agente de documentación** | Redactará y mantendrá la documentación y la bitácora de IA a partir del material real del proyecto |

Estos roles se apoyarán en skills concretas del conjunto "superpowers"
(`subagent-driven-development`, `test-driven-development`, `requesting-code-review`,
`systematic-debugging`); el detalle skill→uso está en [`prompts.md`](prompts.md).

## 3. Roles que se usarán para elaborar la entrega documental

La documentación de cada entrega se producirá también con agentes especializados, para
reducir omisiones y no depender de un único hilo de contexto:

| Rol | Responsabilidad prevista |
|---|---|
| **Agentes de exploración** | Rastrearán el repo y extraerán material real para que la documentación sea verificable y no inventada |
| **Agente redactor de producto** | Redactará visión, personas, MVP y alcance |
| **Agente redactor de arquitectura** | Redactará la arquitectura, contratos y decisiones técnicas |
| **Agente redactor de datos** | Documentará el modelo de datos y las migraciones |
| **Agente redactor de seguridad** | Documentará cifrado de claves, anti-enumeración, SSRF, moderación |
| **Agente redactor de QA/pruebas** | Documentará estrategia de tests, cobertura y validación funcional |
| **Agente redactor de despliegue** | Documentará la dockerización y el manual de puesta en marcha |
| **Agente de bitácora de IA** | Redactará este apartado (flujo, agentes, prompts, decisiones) a partir del material real |

## 4. Mapa con los "posibles subagentes" de la guía §6

La guía §6 enumera una lista de agentes recomendados. Chispa los cubrirá así:

| Subagente sugerido (guía §6) | Cobertura prevista en Chispa |
|---|---|
| Agente de producto y PRD | Redactor de producto |
| Agente de arquitectura | Redactor de arquitectura + planificador de briefs |
| Agente de frontend | Implementador en las tareas de frontend (onboarding, UI de lecciones/cuentos, QR) |
| Agente de backend | Implementador en las tareas de backend (lecciones, config de IA, cuentos, imágenes, contraseña) |
| Agente de datos | Implementador + revisión de migraciones Alembic no destructivas |
| Agente de pruebas | Tests-primero en cada brief + validación funcional real |
| Agente de seguridad OWASP | Revisiones de cifrado, anti-enumeración y SSRF |
| Agente de revisión de PR | Doble capa spec + calidad en cada tarea |
| Agente de documentación | Redactores de la entrega + agente de bitácora de IA |

## 5. Límite explícito: la IA no decidirá sola

Los agentes propondrán y revisarán, pero las **decisiones finales quedarán registradas y
justificadas** por una persona (ver serie AI-LOG en [`decisiones.md`](decisiones.md)). Se
prevén tres patrones de decisión humana sobre las propuestas de la IA:

- **Aceptar un hallazgo y aplicarlo** como corrección inmediata.
- **Aceptar un hallazgo pero dejarlo abierto y documentado** cuando no sea bloqueante.
- **Aprobar una desviación del brief** cuando esté justificada técnicamente y documentada.

Este ida y vuelta **revisión → corrección → decisión justificada** será la evidencia central
del uso estructurado y responsable de la IA que pide la guía. La bitácora completa de esas
decisiones se irá rellenando durante las Entregas 2 y 3.
