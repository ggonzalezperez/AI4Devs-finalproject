# Índice de desarrollo — Chispa (SDD)

Registro navegable del desarrollo dirigido por specs (Spec/Subagent-Driven Development).
Cada tarea tiene un **brief** (spec/plan previo) y un **report** (qué se implementó, tests, review).

- Ledger maestro con commits: [progress.md](progress.md)
- 52 tareas · todas completadas y fusionadas a `main`

---

## Plan 2 — Onboarding del frontend

| Tarea | Descripción | Brief | Report |
|---|---|---|---|
| 1 | Scaffold frontend (Vite + React + TS + Vitest) | [brief](briefs/task-1-brief.md) | [report](reports/task-1-report.md) |
| 2 | Tokens de diseño + primitivas UI (Button, ScreenCard) | [brief](briefs/task-2-brief.md) | [report](reports/task-2-report.md) |
| 3 | Cliente de API tipado + almacenamiento de token | [brief](briefs/task-3-brief.md) | [report](reports/task-3-report.md) |
| 4 | API de auth + contexto de sesión | [brief](briefs/task-4-brief.md) | [report](reports/task-4-report.md) |
| 5 | Enrutado con rutas protegidas | [brief](briefs/task-5-brief.md) | [report](reports/task-5-report.md) |
| 6 | Pantallas de crear familia y login | [brief](briefs/task-6-brief.md) | [report](reports/task-6-report.md) |
| 7 | Añadir/elegir explorador + acceso del niño con PIN | [brief](briefs/task-7-brief.md) | [report](reports/task-7-report.md) |
| 8 | CORS backend + CI del frontend + README | [brief](briefs/task-8-brief.md) | [report](reports/task-8-report.md) |
| i18n | Multilenguaje (es/en, detección + selección) | [brief](briefs/task-i18n-brief.md) | [report](reports/task-i18n-report.md) |
| UX | Arreglo PIN + confirmaciones + pulido | [brief](briefs/task-ux-brief.md) | [report](reports/task-ux-report.md) |

## Plan 3 — Núcleo (lecciones + grafo de conocimiento)

### Backend
| Tarea | Descripción | Brief | Report |
|---|---|---|---|
| A1 | Modelos Lesson/KnowledgeNode + auth de niño + migración | [brief](briefs/task-A1-brief.md) | [report](reports/task-A1-report.md) |
| A2 | LessonGenerator (interfaz) + stub + moderación | [brief](briefs/task-A2-brief.md) | [report](reports/task-A2-report.md) |
| A3 | Endpoints de lecciones (generar + obtener) | [brief](briefs/task-A3-brief.md) | [report](reports/task-A3-report.md) |
| A4 | Responder reto + actualizar grafo de conocimiento | [brief](briefs/task-A4-brief.md) | [report](reports/task-A4-report.md) |
| A5 | Endpoints GET /me/knowledge y /me/suggestions | [brief](briefs/task-A5-brief.md) | [report](reports/task-A5-report.md) |

### Frontend
| Tarea | Descripción | Brief | Report |
|---|---|---|---|
| B1 | Cliente API del niño (núcleo) | [brief](briefs/task-B1-brief.md) | [report](reports/task-B1-report.md) |
| B2 | Pantalla "Encender la chispa" (Spark) | [brief](briefs/task-B2-brief.md) | [report](reports/task-B2-report.md) |
| B3 | Pantalla de Lección y Reto (quiz) | [brief](briefs/task-B3-brief.md) | [report](reports/task-B3-report.md) |
| B4 | "Mis conocimientos" (archipiélago) + cableado | [brief](briefs/task-B4-brief.md) | [report](reports/task-B4-report.md) |

## Plan 4 — IA multi-proveedor configurable + Docker

### Backend
| Tarea | Descripción | Brief | Report |
|---|---|---|---|
| C1 | Cifrado (Fernet) + FamilyAIConfig + migración | [brief](briefs/task-C1-brief.md) | [report](reports/task-C1-report.md) |
| C2 | Catálogo de modelos + recomendador por hardware | [brief](briefs/task-C2-brief.md) | [report](reports/task-C2-report.md) |
| C3 | GET/PUT de config de IA por familia (clave cifrada) | [brief](briefs/task-C3-brief.md) | [report](reports/task-C3-report.md) |
| C4 | Adaptadores de proveedor (HTTP) + fábrica con fallback | [brief](briefs/task-C4-brief.md) | [report](reports/task-C4-report.md) |
| C5 | Conectar lesson_service a la config por familia | [brief](briefs/task-C5-brief.md) | [report](reports/task-C5-report.md) |

### Frontend (panel de padres)
| Tarea | Descripción | Brief | Report |
|---|---|---|---|
| D1 | Cliente API de configuración de IA | [brief](briefs/task-D1-brief.md) | [report](reports/task-D1-report.md) |
| D2 | Panel de configuración de IA + ruta + i18n | [brief](briefs/task-D2-brief.md) | [report](reports/task-D2-report.md) |
| E1 | Dockerización (compose) + manual + README | [brief](briefs/task-E1-brief.md) | [report](reports/task-E1-report.md) |
| UX1 | Mejorar UI/UX del panel de IA | [brief](briefs/task-ux1-brief.md) | [report](reports/task-ux1-report.md) |
| UX2 | Separar sesión de familia y de niño | [brief](briefs/task-ux2-brief.md) | [report](reports/task-ux2-report.md) |
| UX3 | Endpoint GET /me/profile | [brief](briefs/task-ux3-brief.md) | [report](reports/task-ux3-report.md) |
| UX4 | Cabecera del mundo del niño + legibilidad | [brief](briefs/task-ux4-brief.md) | [report](reports/task-ux4-report.md) |
| UX5 | Info/ayuda en onboarding | [brief](briefs/task-ux5-brief.md) | [report](reports/task-ux5-report.md) |

## Biblioteca de cuentos + aprobación parental

| Tarea | Descripción | Brief | Report |
|---|---|---|---|
| S1 | Modelo Story + stub generator + servicio + migración | [brief](briefs/task-S1-brief.md) | [report](reports/task-S1-report.md) |
| S2+S3 | Endpoints de cuentos (crear/leer + aprobar/editar/rechazar) | [brief](briefs/task-S2S3-brief.md) | [report](reports/task-S2S3-report.md) |
| S4 | Frontend — biblioteca y lector del niño | [brief](briefs/task-S4-brief.md) | [report](reports/task-S4-report.md) |
| S5 | Frontend — panel de aprobación de la familia | [brief](briefs/task-S5-brief.md) | [report](reports/task-S5-report.md) |

## Avatares del niño

| Tarea | Descripción | Brief | Report |
|---|---|---|---|
| Avatar-IA | Generar avatar con IA (reusa costura de imagen) | [brief](briefs/task-avatar-ai-brief.md) | [report](reports/task-avatar-ai-report.md) |
| Avatar-wiring | Cableado del avatar (frontend + /me/profile) | [brief](briefs/task-avatar-wiring-brief.md) | [report](reports/task-avatar-wiring-report.md) |

## Lecciones ricas + conversación tipo chat

| Tarea | Descripción | Brief | Report |
|---|---|---|---|
| B1a | Lecciones ricas backend (prompt por edad + follow_ups) | [brief](briefs/task-b1a-lecciones-backend-brief.md) | [report](reports/task-b1a-report.md) |
| B1b | Lecciones conversacionales frontend (chips) | [brief](briefs/task-b1b-lecciones-frontend-brief.md) | [report](reports/task-b1b-report.md) |
| B2a | Chat backend (hilos + contexto + islas automáticas) | [brief](briefs/task-b2a-chat-backend-brief.md) | [report](reports/task-b2a-report.md) |
| B2b | Chat frontend | [brief](briefs/task-b2b-chat-frontend-brief.md) | [report](reports/task-b2b-report.md) |
| B2c | Abrir la conversación al pinchar una isla | [brief](briefs/task-b2c-island-conversation-brief.md) | [report](reports/task-b2c-report.md) |
| B3-buscador | Buscador del archipiélago | [brief](briefs/task-b3-buscador-brief.md) | [report](reports/task-b3-buscador-report.md) |

## Imágenes en lecciones

| Tarea | Descripción | Brief | Report |
|---|---|---|---|
| IMG-1 | Generación de imágenes (backend: HF/SDXL-local/OpenAI/Gemini) | [brief](briefs/task-img1-backend-brief.md) | [report](reports/task-img1-report.md) |
| IMG-2a | Config de imagen en el panel de IA (backend) | [brief](briefs/task-img2a-config-backend-brief.md) | [report](reports/task-img2a-report.md) |
| IMG-2b | Config + render en el chat (frontend) | [brief](briefs/task-img2b-frontend-brief.md) | [report](reports/task-img2b-report.md) |

## Voz y accesibilidad

| Tarea | Descripción | Brief | Report |
|---|---|---|---|
| Voz | Dictar la pregunta con micrófono (Web Speech API) | [brief](briefs/task-voz-brief.md) | [report](reports/task-voz-report.md) |
| TTS | Leer la lección en voz alta (Web Speech Synthesis) | [brief](briefs/task-tts-brief.md) | [report](reports/task-tts-report.md) |

## Conectar dispositivo (LAN)

| Tarea | Descripción | Brief | Report |
|---|---|---|---|
| QR | Conectar móvil dentro de la app (QR + URL) | [brief](briefs/task-qr-brief.md) | [report](reports/task-qr-report.md) |

## Contraseña (cambio + recuperación)

| Tarea | Descripción | Brief | Report |
|---|---|---|---|
| PWD-a | Cambiar y recuperar contraseña (backend) | [brief](briefs/task-pwd-a-backend-brief.md) | [report](reports/task-pwd-a-report.md) |
| PWD-b | Cambiar y recuperar contraseña (frontend) | [brief](briefs/task-pwd-b-frontend-brief.md) | [report](reports/task-pwd-b-report.md) |
