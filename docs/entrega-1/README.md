# Entrega 1 — Producto y diseño técnico · Chispa ✨

> **Máster LIDR – AI4Devs · Proyecto Final** · Alumno: **Germán González Pérez** · Fecha: **22 de julio de 2026**
>
> Esta entrega es **documental y previa a la implementación**: define **qué se va a construir** (producto),
> **cómo** (diseño técnico) y **con qué papel de la IA**, como paso anterior a escribir el código. No incluye código.

> **Chispa ayudará a los niños a aprender desde su curiosidad, convirtiendo cada pregunta en una pequeña aventura
> de conocimiento adaptada a su edad, segura para la familia y acumulada en su propio mapa de aprendizaje.**

**Chispa** será una app web de **aprendizaje por curiosidad para niños**: dentro de una cuenta familiar, cada niño
(perfil con PIN) encenderá una "chispa" (una pregunta), recibirá una mini-lección adaptada a su edad, la reforzará
con un reto, y cada tema se volverá una "isla" de su archipiélago de conocimiento (su **mapa de aprendizaje vivo**).
Los padres supervisarán y aprobarán. No es una app de deberes ni una enciclopedia con IA: es un **espacio personal
de descubrimiento** con memoria pedagógica.

---

## 📂 Índice de la entrega

### 00 · Resumen
- [**00-resumen-proyecto.md**](00-resumen-proyecto.md) — Identificación, descripción breve, resumen ejecutivo y enlaces.

### 01 · Producto
- [problema-y-usuarios.md](01-product/problema-y-usuarios.md) — Situación actual, actores afectados, impacto.
- [prd.md](01-product/prd.md) — Propuesta de valor, objetivos y métricas de éxito.
- [alcance.md](01-product/alcance.md) — MVP, épicas, fuera de alcance, riesgos y supuestos.
- [historias-usuario.md](01-product/historias-usuario.md) — US1–US11 (6 épicas) con plantilla DoR y criterios de aceptación Gherkin.
- [requisitos.md](01-product/requisitos.md) — Requisitos funcionales (RF) y no funcionales (RNF) en formato tabular + **matriz de trazabilidad HU↔RF** (base para pruebas funcionales).

### 02 · Diseño técnico
- [arquitectura.md](02-technical-design/arquitectura.md) — Contexto, componentes, flujo de datos y *seams* de IA (diagramas Mermaid).
- [modelo-datos.md](02-technical-design/modelo-datos.md) — Diagrama ER, 7 entidades y 11 migraciones aditivas.
- [contratos-api.md](02-technical-design/contratos-api.md) — Todos los endpoints (método/ruta/auth/req/resp/códigos).
- [seguridad.md](02-technical-design/seguridad.md) — JWT tipado, cifrado, moderación, aislamiento, SSRF, OWASP.
- [decisiones-tecnologicas.md](02-technical-design/decisiones-tecnologicas.md) — Stack y justificación.
- [adr/](02-technical-design/adr/) — 7 Architecture Decision Records:
  - [ADR-001 — Seams de IA + fallback al stub](02-technical-design/adr/ADR-001-seams-ia-fallback-stub.md)
  - [ADR-002 — JWT tipado familia/niño](02-technical-design/adr/ADR-002-jwt-tipado-familia-nino.md)
  - [ADR-003 — Cifrado Fernet de claves de IA](02-technical-design/adr/ADR-003-cifrado-fernet-claves-ia.md)
  - [ADR-004 — Conversación en hilos + islas automáticas](02-technical-design/adr/ADR-004-conversacion-hilos-islas-auto.md)
  - [ADR-005 — Aprobación parental de cuentos](02-technical-design/adr/ADR-005-aprobacion-parental-cuentos.md)
  - [ADR-006 — Migraciones Alembic aditivas](02-technical-design/adr/ADR-006-migraciones-aditivas.md)
  - [ADR-007 — Degradación elegante transversal](02-technical-design/adr/ADR-007-degradacion-elegante.md)

### 03 · Pruebas
- [estrategia-pruebas.md](03-testing/estrategia-pruebas.md) — Pirámide, cobertura por riesgo, CI, herramientas.
- [casos-aceptacion.md](03-testing/casos-aceptacion.md) — BDD por historia trazado a los tests reales.

### 04 · Entrega
- [despliegue.md](04-delivery/despliegue.md) — Docker Compose, LAN + QR, entornos, CI/CD.
- [demo.md](04-delivery/demo.md) — Guion de demo E2E y evidencias.

### 05 · Bitácora de IA
- [flujo-trabajo-ia.md](05-ai-log/flujo-trabajo-ia.md) — Método SDD / subagent-driven (brief→implementación→review).
- [agentes.md](05-ai-log/agentes.md) — Roles de subagentes usados.
- [prompts.md](05-ai-log/prompts.md) — Playbook de prompts para regenerar la entrega desde un *discovery* (12 secciones) + patrón de brief/spec y skills empleadas.
- [decisiones.md](05-ai-log/decisiones.md) — Entradas AI-LOG (hallazgos, correcciones, validación).

---

## ✅ Checklist de cumplimiento (guía académica §15)

### Producto
- [x] El problema está claramente definido → [problema-y-usuarios.md](01-product/problema-y-usuarios.md)
- [x] El usuario objetivo está identificado → [problema-y-usuarios.md](01-product/problema-y-usuarios.md)
- [x] La propuesta de valor es comprensible → [prd.md](01-product/prd.md)
- [x] El MVP tiene historias principales (11 en 6 épicas) → [alcance.md](01-product/alcance.md)
- [x] Las historias opcionales no bloquean la entrega → [alcance.md](01-product/alcance.md)
- [x] Cada historia tiene criterios verificables → [historias-usuario.md](01-product/historias-usuario.md)

### Técnica
- [x] La arquitectura responde al problema → [arquitectura.md](02-technical-design/arquitectura.md)
- [x] Los componentes tienen responsabilidades claras → [arquitectura.md](02-technical-design/arquitectura.md)
- [x] El modelo de datos está documentado → [modelo-datos.md](02-technical-design/modelo-datos.md)
- [x] Las decisiones tecnológicas están justificadas → [decisiones-tecnologicas.md](02-technical-design/decisiones-tecnologicas.md) + [adr/](02-technical-design/adr/)
- [x] Existe una estrategia de pruebas → [estrategia-pruebas.md](03-testing/estrategia-pruebas.md)
- [x] Se han considerado seguridad y privacidad → [seguridad.md](02-technical-design/seguridad.md)

### Inteligencia artificial
- [x] Se documentan herramientas, agentes y skills → [flujo-trabajo-ia.md](05-ai-log/flujo-trabajo-ia.md) + [agentes.md](05-ai-log/agentes.md)
- [x] Se conservan los prompts/instrucciones relevantes → [prompts.md](05-ai-log/prompts.md)
- [x] Se define el formato de bitácora para registrar alucinaciones y correcciones → [decisiones.md](05-ai-log/decisiones.md)
- [x] Se define cómo se validarán las salidas de IA → [flujo-trabajo-ia.md](05-ai-log/flujo-trabajo-ia.md) (revisión en dos capas + TDD)
- [x] La IA forma parte del proceso, no solo de la redacción → método SDD / subagentes ([flujo-trabajo-ia.md](05-ai-log/flujo-trabajo-ia.md))

### Entrega
- [x] Documentación estructurada según la plantilla de la guía (§8)
- [x] Repositorio accesible (privado; acceso al TA a solicitud)
- [ ] Sin secretos ni datos confidenciales — verificar antes del envío (ver [despliegue.md](04-delivery/despliegue.md))
- [ ] Pull request creado — paso de envío
- [ ] Formulario de entrega enviado — paso de envío
- [ ] Evidencia de la entrega guardada — paso de envío

> Los cuatro últimos son pasos del proceso de envío (no de la redacción); se marcan al entregar.

---

## 🗺️ Mapa de trazabilidad (resumen)

Cada historia de usuario se realizará en estas pantallas y endpoints, y se validará con estas pruebas (realización prevista):

| Épica | Historias | Pantallas previstas | Endpoints previstos | Pruebas previstas |
|---|---|---|---|---|
| E1 Onboarding y perfiles | US1 | Welcome, CreateFamily, Login, FamilyLanding, AddExplorer, ChildAccess, ChangePassword, ResetPassword | `/auth/*`, `/children/*` | test_auth, test_password, test_children, AddExplorer/ChildAccess.test |
| E2 Bucle de aprendizaje | US2, US3, US4 | Spark, LessonScreen | `/lessons`, `/lessons/{id}/ask`, `/answer` | test_lessons_api, test_answer_api, test_conversation |
| E3 Conocimiento vivo | US7, US8 | MyKnowledge, LessonScreen | `/me/knowledge`, `/lessons/{id}/thread` | test_conversation, MyKnowledge.test |
| E4 Cuentos | US9 | StoryLibrary, StoryReader, FamilyStories | `/me/stories`, `/family/stories` | test_story_api |
| E5 IA configurable | US10 | AIConfigPanel | `/family/ai-config`, `/catalog`, `/recommend` | test_ai_config_api, test_ai_config_crud |
| E6 Plataforma y accesibilidad | US5, US6, US11 | WhoExplores, FamilyPanel, ExitChildSession, ConnectDevice, ChildAvatar | `/children/{id}/profile`, `/children/{id}/knowledge`, `/auth/verify-password`, `/children/{id}/avatar/generate` | test_family_panel, test_password, test_avatar_ai, test_images |

Detalle completo en [historias-usuario.md](01-product/historias-usuario.md). La **matriz HU ↔ RF ↔ prueba funcional** (trazabilidad y base de pruebas) está en [requisitos.md](01-product/requisitos.md).
